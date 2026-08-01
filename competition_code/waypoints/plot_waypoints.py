import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
import os

# ==========================================
# CONFIGURATION
# ==========================================
CAR_WIDTH = 2.1634500027          # Width of the car in meters
CAR_LENGTH = 4.7917795181         # Length of the car in meters
WALL_MARGIN = 2.0                 # Minimum distance to keep from track walls
MIN_WAYPOINT_DIST = 0.2           # Minimum allowed distance between consecutive waypoints in meters
TRANSLATE_STEP = 0.5              # Distance (in meters) to move selected waypoints per arrow key press
ROTATE_STEP = 2.0                 # Degrees to rotate selected waypoints per key press ('[' or ']')
ROTATION_PIVOT = 'bottom'         # Point to rotate around. Options: 'center', 'top', 'bottom'
# ==========================================

class TrackEditor:
    def __init__(self, reference_filepath, target_filepath_1, target_filepath_2, car_width=CAR_WIDTH, car_length=CAR_LENGTH, wall_margin=WALL_MARGIN, min_dist=MIN_WAYPOINT_DIST):
        self.ref_filepath = reference_filepath
        self.car_width = car_width
        self.car_length = car_length
        self.wall_margin = wall_margin
        self.min_dist = min_dist
        
        self.edit_mode = 'inner'
        self.show_car_boxes = False
        self.current_mouse_event = None
        self.active_track_idx = 0 # 0 for Path 1, 1 for Path 2
        
        # Selection tools
        self.selected_indices = []
        self.selection_start = None
        
        # 1. Load Reference Data
        self.ref_x, self.ref_y, self.ref_widths, *_ = self._load_npz(reference_filepath)
        if self.ref_widths is None:
            raise ValueError(f"Reference file '{reference_filepath}' must contain 'lane_widths' to draw track bounds.")
            
        # 2. Load Target Data for BOTH tracks
        self.tracks = []
        self._init_track_data(target_filepath_1)
        self._init_track_data(target_filepath_2)

        # 3. Setup Figure
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.fig.canvas.manager.set_window_title(f"Dual Racing Line Editor")
        
        # 4. Draw Static Reference Track
        self._plot_reference_track()
        
        # 5. Draw Editable Target Tracks
        # Track 1 Visuals (Blue / Red)
        self.line1, = self.ax.plot(self.tracks[0]['x'], self.tracks[0]['y'], 'b-', linewidth=1.5, zorder=4, label="Path 1")
        self.scatter1 = self.ax.scatter([], [], zorder=5, edgecolors='black', linewidths=0.5)
        
        # Track 2 Visuals (Purple / Cyan)
        self.line2, = self.ax.plot(self.tracks[1]['x'], self.tracks[1]['y'], color='purple', linestyle='-', linewidth=1.5, zorder=4, label="Path 2")
        self.scatter2 = self.ax.scatter([], [], zorder=5, edgecolors='black', linewidths=0.5)
        
        self.lines = [self.line1, self.line2]
        self.scatters = [self.scatter1, self.scatter2]

        # Car Boxes
        car_widths_array = np.full_like(self.tracks[0]['x'], self.car_width)
        car_segments = self._calculate_perpendicular_segments(self.tracks[0]['x'], self.tracks[0]['y'], car_widths_array)
        self.car_lines = LineCollection(car_segments, colors='green', linewidths=2.0, alpha=0.8, zorder=3)
        self.ax.add_collection(self.car_lines)

        car_box_segments = self._calculate_car_boxes(self.tracks[0]['x'], self.tracks[0]['y'])
        self.car_boxes = LineCollection(car_box_segments, colors='magenta', linewidths=1.0, alpha=0.6, zorder=3.5)
        self.car_boxes.set_visible(self.show_car_boxes)
        self.ax.add_collection(self.car_boxes)

        # Selection Box
        self.selection_rect = Rectangle((0, 0), 1, 1, fill=True, color='yellow', alpha=0.2, linestyle='--', edgecolor='black', visible=False, zorder=10)
        self.ax.add_patch(self.selection_rect)

        self._update_scatter_points()
        
        self.ax.axis('equal')
        self.ax.grid(True, linestyle='--', alpha=0.4)
        self.ax.set_xlabel("X Coordinate (m)")
        self.ax.set_ylabel("Y Coordinate (m)")
        self.ax.legend()
        
        self._update_title()
        
        # 6. State Variables
        self._ind = None
        self._dragging = False

        # 7. Connect Events
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll) 

    def _init_track_data(self, filepath):
        target_data = self._load_npz(filepath, keep_original=True)
        self.tracks.append({
            'x': target_data[0],
            'y': target_data[1],
            'widths': target_data[2],
            'original_dict': target_data[3],
            'load_mode': target_data[4],
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'undo_stack': []
        })

    def _update_scatter_points(self):
        for idx in range(2):
            x, y = self.tracks[idx]['x'], self.tracks[idx]['y']
            
            # Base colors depending on the track
            base_color = 'red' if idx == 0 else 'cyan'
            colors = [base_color] * len(x)
            
            if len(x) > 0:
                colors[0] = 'green'
                colors[-1] = 'orange'
                
            # Highlight selected points for the active track
            if idx == self.active_track_idx:
                for s_idx in self.selected_indices:
                    if s_idx < len(colors):
                        colors[s_idx] = 'yellow'
            
            sizes = [15] * len(x)
            if len(x) > 0:
                sizes[0] = sizes[-1] = 50
                
            self.scatters[idx].set_offsets(np.column_stack([x, y]))
            self.scatters[idx].set_color(colors)
            self.scatters[idx].set_sizes(sizes)
            
            # Dim the inactive track
            alpha = 1.0 if idx == self.active_track_idx else 0.3
            self.lines[idx].set_alpha(alpha)
            self.scatters[idx].set_alpha(alpha)

    def _calculate_lap_length(self, track_idx):
        x, y = self.tracks[track_idx]['x'], self.tracks[track_idx]['y']
        if len(x) < 2:
            return 0.0
        return float(np.sum(np.hypot(np.diff(x), np.diff(y))))

    def _update_title(self):
        mode_str = "Middle" if self.edit_mode == 'inner' else "Start/End"
        active_t = self.tracks[self.active_track_idx]
        lap_len = self._calculate_lap_length(self.active_track_idx)
        
        title_text = (
            f"Active: PATH {self.active_track_idx + 1} ({active_t['filename']}) | Mode: {mode_str} | Dist: {lap_len:.2f} m\n"
            f"Arrows=Move | [/]=Rotate | d=Del | e=Clean | b=Box | z=Undo | o/p=Opt"
        )
        self.ax.set_title(title_text, fontsize=9.5, color='black', fontweight='normal')
        self.fig.canvas.draw_idle()

    def _load_npz(self, filepath, keep_original=False):
        data = np.load(filepath)
        original_dict = {key: data[key].copy() for key in data.files} if keep_original else None
        
        load_mode = None
        if 'locations' in data:
            locs = data['locations'].astype(float)
            x, y = locs[:, 0].copy(), locs[:, 1].copy()
            load_mode = 'locations'
        elif 'x' in data and 'y' in data:
            x, y = data['x'].astype(float).copy(), data['y'].astype(float).copy()
            load_mode = 'xy'
        elif 'waypoints' in data:
            x, y = data['waypoints'][:, 0].astype(float).copy(), data['waypoints'][:, 1].astype(float).copy()
            load_mode = 'waypoints'
        else:
            first_key = data.files[0]
            x, y = data[first_key][:, 0].astype(float).copy(), data[first_key][:, 1].astype(float).copy()
            load_mode = 'first_key'

        widths = data['lane_widths'].flatten() if 'lane_widths' in data else None
        return x, y, widths, original_dict, load_mode

    def _plot_reference_track(self):
        dx = np.gradient(self.ref_x)
        dy = np.gradient(self.ref_y)
        
        mags = np.hypot(dx, dy)
        mags[mags == 0] = 1e-6 
        
        nx = -dy / mags
        ny = dx / mags
        half_w = self.ref_widths / 2.0
        
        left_x = self.ref_x - nx * half_w
        left_y = self.ref_y - ny * half_w
        right_x = self.ref_x + nx * half_w
        right_y = self.ref_y + ny * half_w
        
        self.ax.plot(left_x, left_y, 'k-', linewidth=2, zorder=1, label="Track Bounds")
        self.ax.plot(right_x, right_y, 'k-', linewidth=2, zorder=1)

    def _calculate_perpendicular_segments(self, x, y, widths_array):
        dx = np.gradient(x)
        dy = np.gradient(y)
        
        mags = np.hypot(dx, dy)
        mags[mags == 0] = 1e-6 
        
        nx = -dy / mags
        ny = dx / mags
        
        half_w = widths_array / 2.0
        
        x1, y1 = x - nx * half_w, y - ny * half_w
        x2, y2 = x + nx * half_w, y + ny * half_w
        
        return np.stack([np.column_stack([x1, y1]), np.column_stack([x2, y2])], axis=1)

    def _calculate_car_boxes(self, x, y):
        dx = np.gradient(x)
        dy = np.gradient(y)
        
        mags = np.hypot(dx, dy)
        mags[mags == 0] = 1e-6
        
        fx, fy = dx / mags, dy / mags
        sx, sy = -fy, fx
        
        half_l = self.car_length / 2.0
        half_w = self.car_width / 2.0
        
        boxes = []
        for i in range(len(x)):
            cx, cy = x[i], y[i]
            c1 = (cx + fx[i]*half_l + sx[i]*half_w, cy + fy[i]*half_l + sy[i]*half_w)
            c2 = (cx + fx[i]*half_l - sx[i]*half_w, cy + fy[i]*half_l - sy[i]*half_w)
            c3 = (cx - fx[i]*half_l - sx[i]*half_w, cy - fy[i]*half_l - sy[i]*half_w)
            c4 = (cx - fx[i]*half_l + sx[i]*half_w, cy - fy[i]*half_l + sy[i]*half_w)
            boxes.append(np.array([c1, c2, c3, c4, c1]))
            
        return boxes

    def _refresh_visuals(self):
        for idx in range(2):
            self.lines[idx].set_data(self.tracks[idx]['x'], self.tracks[idx]['y'])
            
        self._update_scatter_points()
        
        active_x = self.tracks[self.active_track_idx]['x']
        active_y = self.tracks[self.active_track_idx]['y']
        
        car_widths_array = np.full_like(active_x, self.car_width)
        self.car_lines.set_segments(self._calculate_perpendicular_segments(active_x, active_y, car_widths_array))
        
        if self.show_car_boxes:
            self.car_boxes.set_segments(self._calculate_car_boxes(active_x, active_y))
            
        self._update_title()

    def push_undo(self):
        active_t = self.tracks[self.active_track_idx]
        active_t['undo_stack'].append((active_t['x'].copy(), active_t['y'].copy()))
        if len(active_t['undo_stack']) > 50:
            active_t['undo_stack'].pop(0)

    def clean_close_waypoints(self, min_distance=None):
        if min_distance is None:
            min_distance = self.min_dist

        active_t = self.tracks[self.active_track_idx]
        x, y = active_t['x'], active_t['y']

        if len(x) <= 3:
            return

        keep_indices = [0]
        for i in range(1, len(x) - 1):
            last_kept_idx = keep_indices[-1]
            dist = np.hypot(x[i] - x[last_kept_idx], y[i] - y[last_kept_idx])
            if dist >= min_distance:
                keep_indices.append(i)

        if keep_indices[-1] != len(x) - 1:
            dist_to_last = np.hypot(x[-1] - x[keep_indices[-1]], y[-1] - y[keep_indices[-1]])
            if dist_to_last < min_distance and len(keep_indices) > 1:
                keep_indices.pop()
            keep_indices.append(len(x) - 1)

        removed_count = len(x) - len(keep_indices)
        if removed_count > 0:
            active_t['x'] = x[keep_indices]
            active_t['y'] = y[keep_indices]
            
            # Clear selected indices as array structure changed
            self.selected_indices = []
            
            print(f"Path {self.active_track_idx + 1}: Cleaned up {removed_count} waypoints closer than {min_distance}m!")
            self._refresh_visuals()

    def get_closest_point(self, event, ignore_mode=False):
        if event is None or event.xdata is None or event.ydata is None: 
            return None
            
        xlim = self.ax.get_xlim()
        threshold = (xlim[1] - xlim[0]) * 0.02
        
        active_t = self.tracks[self.active_track_idx]
        x, y = active_t['x'], active_t['y']
        
        if ignore_mode:
            distances = np.hypot(x - event.xdata, y - event.ydata)
            closest_idx = np.argmin(distances)
            if distances[closest_idx] < threshold:
                return closest_idx
            return None

        if self.edit_mode == 'inner':
            valid_x, valid_y = x[1:-1], y[1:-1]
            if len(valid_x) == 0:
                return None
                
            distances = np.hypot(valid_x - event.xdata, valid_y - event.ydata)
            closest_valid_idx = np.argmin(distances)
            
            if distances[closest_valid_idx] < threshold:
                return closest_valid_idx + 1
                
        elif self.edit_mode == 'ends':
            ends_x = np.array([x[0], x[-1]])
            ends_y = np.array([y[0], y[-1]])
            
            distances = np.hypot(ends_x - event.xdata, ends_y - event.ydata)
            closest_valid_idx = np.argmin(distances)
            
            if distances[closest_valid_idx] < threshold:
                return 0 if closest_valid_idx == 0 else len(x) - 1
                
        return None

    def delete_waypoint(self, idx):
        active_t = self.tracks[self.active_track_idx]
        if idx is None or len(active_t['x']) <= 3:
            return

        self.push_undo()

        active_t['x'] = np.delete(active_t['x'], idx)
        active_t['y'] = np.delete(active_t['y'], idx)
        
        # Clear selected indices since the array shape changed
        self.selected_indices = []
        
        print(f"Path {self.active_track_idx + 1}: Deleted waypoint {idx}. ({len(active_t['x'])} waypoints remaining)")
        self._refresh_visuals()

    def on_scroll(self, event):
        if event.inaxes != self.ax:
            return

        base_scale = 1.15
        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            return

        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        xdata = event.xdata
        ydata = event.ydata

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

        self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        self.ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        
        self.fig.canvas.draw_idle()

    def on_press(self, event):
        if event.inaxes != self.ax or event.button != 1: 
            return
        
        self._ind = self.get_closest_point(event)
        
        if self._ind is not None:
            # Clicked on a point - start standard drag
            self.push_undo()
            self._dragging = True
            
            # If the user clicks a point not in selection, clear selection
            if self._ind not in self.selected_indices:
                self.selected_indices = []
                self._refresh_visuals()
        else:
            # Clicked on empty space - clear selection and start box drag
            self.selected_indices = []
            self.selection_start = (event.xdata, event.ydata)
            self.selection_rect.set_xy(self.selection_start)
            self.selection_rect.set_width(0)
            self.selection_rect.set_height(0)
            self.selection_rect.set_visible(True)
            self._refresh_visuals()

    def on_motion(self, event):
        self.current_mouse_event = event
        if event.inaxes != self.ax: 
            return
        
        # Handle dragging a single point
        if self._dragging and self._ind is not None:
            active_t = self.tracks[self.active_track_idx]
            active_t['x'][self._ind] = event.xdata
            active_t['y'][self._ind] = event.ydata
            self._refresh_visuals()
            
        # Handle box selection dragging
        elif self.selection_start is not None and event.xdata is not None and event.ydata is not None:
            x0, y0 = self.selection_start
            x1, y1 = event.xdata, event.ydata
            
            self.selection_rect.set_xy((min(x0, x1), min(y0, y1)))
            self.selection_rect.set_width(abs(x1 - x0))
            self.selection_rect.set_height(abs(y1 - y0))
            self.fig.canvas.draw_idle()

    def on_release(self, event):
        if self._dragging:
            self._dragging = False
            self._ind = None
        elif self.selection_start is not None and event.xdata is not None and event.ydata is not None:
            # Finalize box selection
            x0, y0 = self.selection_start
            x1, y1 = event.xdata, event.ydata
            xmin, xmax = min(x0, x1), max(x0, x1)
            ymin, ymax = min(y0, y1), max(y0, y1)
            
            active_t = self.tracks[self.active_track_idx]
            x_pts, y_pts = active_t['x'], active_t['y']
            
            for i in range(len(x_pts)):
                if xmin <= x_pts[i] <= xmax and ymin <= y_pts[i] <= ymax:
                    self.selected_indices.append(i)
            
            self.selection_start = None
            self.selection_rect.set_visible(False)
            
            if self.selected_indices:
                print(f"Path {self.active_track_idx + 1}: Selected {len(self.selected_indices)} waypoints.")
            self._refresh_visuals()
        else:
            # Fallback if dragging exited bounds
            self.selection_start = None
            self.selection_rect.set_visible(False)
            self._refresh_visuals()

    def on_key(self, event):
        # Base keyboard shortcuts
        if event.key == '1':
            self.active_track_idx = 0
            self.selected_indices = [] # Clear selection on switch
            self._refresh_visuals()
            print("Switched to Path 1")
        elif event.key == '2':
            self.active_track_idx = 1
            self.selected_indices = [] # Clear selection on switch
            self._refresh_visuals()
            print("Switched to Path 2")
        elif event.key == 's':
            self.save_data()
        elif event.key == 'e':
            # Note: 'e' now only cleans if no selection (rotation moved to [/]).
            if not self.selected_indices:
                self.push_undo()
                self.clean_close_waypoints()
        elif event.key == 'g':
            self.calculate_and_save_radii()
        elif event.key in ['d', 'delete', 'backspace']:
            target_idx = self.get_closest_point(self.current_mouse_event, ignore_mode=True)
            if target_idx is not None:
                self.delete_waypoint(target_idx)
            elif self.selected_indices:
                # Optional: Handle batch deletion if waypoints are selected
                self.push_undo()
                active_t = self.tracks[self.active_track_idx]
                active_t['x'] = np.delete(active_t['x'], self.selected_indices)
                active_t['y'] = np.delete(active_t['y'], self.selected_indices)
                print(f"Path {self.active_track_idx + 1}: Deleted {len(self.selected_indices)} selected waypoints.")
                self.selected_indices = []
                self._refresh_visuals()
            else:
                print("Hover over a waypoint on the active path to delete it.")
        elif event.key == 'z' or event.key == 'ctrl+z':
            self.undo()
        elif event.key == 't':
            self.edit_mode = 'ends' if self.edit_mode == 'inner' else 'inner'
            self._update_title()
        elif event.key == 'b':
            self.show_car_boxes = not self.show_car_boxes
            self.car_boxes.set_visible(self.show_car_boxes)
            self._refresh_visuals()
        elif event.key == 'escape':
            self.selected_indices = []
            self._refresh_visuals()
        elif event.key == 'o':
            self.optimize_racing_line(fix_endpoints=False, closed_loop=False)
        elif event.key == 'p':
            self.optimize_racing_line(fix_endpoints=False, closed_loop=True)

        # Translation controls (Arrow Keys)
        elif event.key in ['up', 'down', 'left', 'right'] and self.selected_indices:
            self.push_undo()
            active_t = self.tracks[self.active_track_idx]
            
            dx, dy = 0.0, 0.0
            if event.key == 'up':
                dy = TRANSLATE_STEP
            elif event.key == 'down':
                dy = -TRANSLATE_STEP
            elif event.key == 'left':
                dx = -TRANSLATE_STEP
            elif event.key == 'right':
                dx = TRANSLATE_STEP
                
            active_t['x'][self.selected_indices] += dx
            active_t['y'][self.selected_indices] += dy
            self._refresh_visuals()

        # Rotation Controls ([/])
        elif event.key in ['[', ']'] and self.selected_indices:
            self.push_undo()
            active_t = self.tracks[self.active_track_idx]
            
            # Convert degrees to radians ([ = counter-clockwise, ] = clockwise)
            theta = np.radians(ROTATE_STEP) if event.key == '[' else np.radians(-ROTATE_STEP)
            
            x_sel = active_t['x'][self.selected_indices]
            y_sel = active_t['y'][self.selected_indices]
            
            # Determine rotation pivot based on configuration
            if ROTATION_PIVOT == 'top':
                cx = np.mean(x_sel)
                cy = np.max(y_sel)
            elif ROTATION_PIVOT == 'bottom':
                cx = np.mean(x_sel)
                cy = np.min(y_sel)
            else: # 'center' or fallback
                cx = np.mean(x_sel)
                cy = np.mean(y_sel)
            
            # Translate points to origin based on pivot
            dx = x_sel - cx
            dy = y_sel - cy
            
            # Apply 2D rotation matrix
            new_x = dx * np.cos(theta) - dy * np.sin(theta)
            new_y = dx * np.sin(theta) + dy * np.cos(theta)
            
            # Translate back
            active_t['x'][self.selected_indices] = new_x + cx
            active_t['y'][self.selected_indices] = new_y + cy
            
            self._refresh_visuals()

    def calculate_and_save_radii(self):
        active_t = self.tracks[self.active_track_idx]
        print(f"Calculating and saving waypoint radii for Path {self.active_track_idx + 1}...")
        
        x, y = active_t['x'], active_t['y']
        output_lines = []
        num_wp = len(x)
        
        if num_wp < 3:
            print("Not enough waypoints to calculate radii.")
            return

        # ==========================================
        # TUNING PARAMETERS FOR SMOOTHNESS
        # ==========================================
        step = 6 
        smooth_window = 3 
        # ==========================================

        raw_radii = []

        # 1. Calculate raw macro-radii
        for i in range(num_wp):
            p1 = np.array([x[(i - step) % num_wp], y[(i - step) % num_wp]])
            p2 = np.array([x[i], y[i]])
            p3 = np.array([x[(i + step) % num_wp], y[(i + step) % num_wp]])
            
            a = np.linalg.norm(p2 - p3)
            b = np.linalg.norm(p1 - p3)
            c = np.linalg.norm(p1 - p2)
            
            cross = np.abs(np.cross(p2 - p1, p3 - p1))
            
            if cross < 1e-4: 
                radius = 9999
            else:
                radius_exact = (a * b * c) / (2 * cross)
                radius = min(int(np.round(radius_exact)), 9999)
            
            raw_radii.append(radius)
            
        # 2. Apply moving average and write ONLY radii to the output array
        for i in range(num_wp):
            window_vals = []
            for j in range(-smooth_window, smooth_window + 1):
                window_vals.append(raw_radii[(i + j) % num_wp])
            
            smoothed_radius = int(np.mean(window_vals))
            output_lines.append(f"{smoothed_radius}")  # Removed the index number
            
        filename = f"radii_{active_t['filename']}.txt"
        with open(filename, "w") as f:
            f.write("\n".join(output_lines))
        print(f"Successfully saved smoothed radii to {filename}!")
        
        self.ax.set_title(f"RADII SAVED TO {filename}", color='blue', fontweight='bold', fontsize=12)
        self.fig.canvas.draw_idle()
        
        timer = self.fig.canvas.new_timer(interval=2000)
        timer.add_callback(self._update_title)
        timer.start()

    def optimize_racing_line(self, iterations=300, alpha_smooth=0.2, alpha_length=0.1, fix_endpoints=False, closed_loop=False):
        mode_msg = "closed loop" if closed_loop else ("locking endpoints" if fix_endpoints else "including endpoints")
        print(f"Path {self.active_track_idx + 1}: Optimizing racing line (Curvature + Tension) ({mode_msg})...")
        
        self.push_undo()
        active_t = self.tracks[self.active_track_idx]

        ref_dx = np.gradient(self.ref_x)
        ref_dy = np.gradient(self.ref_y)
        ref_mags = np.hypot(ref_dx, ref_dy)
        ref_mags[ref_mags == 0] = 1e-6
        ref_nx = -ref_dy / ref_mags
        ref_ny = ref_dx / ref_mags

        new_x = active_t['x'].copy()
        new_y = active_t['y'].copy()

        start_idx = 1 if fix_endpoints and not closed_loop else 0
        end_idx = len(active_t['x']) - 1 if fix_endpoints and not closed_loop else len(active_t['x'])
        num_pts = len(active_t['x'])

        for _ in range(iterations):
            temp_x = new_x.copy()
            temp_y = new_y.copy()
            
            for i in range(start_idx, end_idx):
                if closed_loop:
                    prev2_i = (i - 2) % num_pts
                    prev_i  = (i - 1) % num_pts
                    next_i  = (i + 1) % num_pts
                    next2_i = (i + 2) % num_pts
                else:
                    prev2_i = max(0, i - 2)
                    prev_i  = max(0, i - 1)
                    next_i  = min(num_pts - 1, i + 1)
                    next2_i = min(num_pts - 1, i + 2)
                
                smooth_x = (-temp_x[prev2_i] + 4 * temp_x[prev_i] + 4 * temp_x[next_i] - temp_x[next2_i]) / 6.0
                smooth_y = (-temp_y[prev2_i] + 4 * temp_y[prev_i] + 4 * temp_y[next_i] - temp_y[next2_i]) / 6.0

                length_x = (temp_x[prev_i] + temp_x[next_i]) / 2.0
                length_y = (temp_y[prev_i] + temp_y[next_i]) / 2.0

                cand_x = temp_x[i] + alpha_smooth * (smooth_x - temp_x[i]) + alpha_length * (length_x - temp_x[i])
                cand_y = temp_y[i] + alpha_smooth * (smooth_y - temp_y[i]) + alpha_length * (length_y - temp_y[i])

                dists = np.hypot(self.ref_x - cand_x, self.ref_y - cand_y)
                closest_idx = np.argmin(dists)

                max_disp = (self.ref_widths[closest_idx] / 2.0) - self.wall_margin
                max_disp = max(0.0, max_disp)

                vec_x = cand_x - self.ref_x[closest_idx]
                vec_y = cand_y - self.ref_y[closest_idx]
                disp = vec_x * ref_nx[closest_idx] + vec_y * ref_ny[closest_idx]

                clamped_disp = np.clip(disp, -max_disp, max_disp)

                new_x[i] = self.ref_x[closest_idx] + clamped_disp * ref_nx[closest_idx]
                new_y[i] = self.ref_y[closest_idx] + clamped_disp * ref_ny[closest_idx]

        active_t['x'] = new_x
        active_t['y'] = new_y
        
        self.clean_close_waypoints()
        self._refresh_visuals()
        print("Optimization complete!")

    def undo(self):
        active_t = self.tracks[self.active_track_idx]
        if not active_t['undo_stack']:
            print(f"Path {self.active_track_idx + 1}: Nothing to undo.")
            return
            
        active_t['x'], active_t['y'] = active_t['undo_stack'].pop()
        
        # Clear selected indices just in case the undo changes array size or shifts points drastically
        self.selected_indices = []
        
        self._refresh_visuals()
        print(f"Path {self.active_track_idx + 1}: Undo successful. ({len(active_t['undo_stack'])} steps remaining)")

    def save_data(self):
        track = self.tracks[self.active_track_idx]
        new_filename = f"output_{track['filename']}"
        save_path = os.path.join(os.path.dirname(track['filepath']), new_filename)
        
        save_dict = track['original_dict'].copy()
        num_points = len(track['x'])

        if 'locations' in save_dict:
            orig_shape = save_dict['locations'].shape
            if orig_shape[1] == 3:
                old_z = save_dict['locations'][:, 2] if len(save_dict['locations']) == num_points else np.zeros(num_points)
                save_dict['locations'] = np.column_stack([track['x'], track['y'], old_z])
            else:
                save_dict['locations'] = np.column_stack([track['x'], track['y']])
        elif track['load_mode'] == 'xy':
            save_dict['x'] = track['x']
            save_dict['y'] = track['y']
        elif track['load_mode'] == 'waypoints':
            save_dict['waypoints'] = np.column_stack([track['x'], track['y']])

        if 'rotations' in save_dict:
            dx = np.gradient(track['x'])
            dy = np.gradient(track['y'])
            yaws = np.arctan2(dy, dx)
            yaws = np.unwrap(yaws)
            
            kernel_size = 3
            kernel = np.ones(kernel_size) / kernel_size
            yaws_padded = np.pad(yaws, (kernel_size//2, kernel_size//2), mode='edge')
            smoothed_yaws = np.convolve(yaws_padded, kernel, mode='valid')
            
            rot_shape = save_dict['rotations'].shape
            if len(rot_shape) == 1 or (len(rot_shape) == 2 and rot_shape[1] == 1):
                save_dict['rotations'] = smoothed_yaws
            elif len(rot_shape) == 2 and rot_shape[1] >= 3:
                new_rots = np.zeros((num_points, rot_shape[1]))
                new_rots[:, -1] = smoothed_yaws
                save_dict['rotations'] = new_rots

        if 'lane_widths' in save_dict:
            save_dict['lane_widths'] = np.full(num_points, self.car_width)

        np.savez(save_path, **save_dict)
        print(f"Saved Active Path ({self.active_track_idx + 1}) to: {save_path}")
        
        self.ax.set_title(f"PATH {self.active_track_idx + 1} SAVED SUCCESSFULLY", color='green', fontweight='bold', fontsize=12)
        self.fig.canvas.draw_idle()
        
        timer = self.fig.canvas.new_timer(interval=2000)
        timer.add_callback(self._update_title)
        timer.start()

if __name__ == "__main__":
    REFERENCE_TRACK = "competition_code/waypoints/Monza.npz"
    EDITABLE_PATH_1 = "competition_code/waypoints/output_theWaypoints.npz"
    EDITABLE_PATH_2 = "competition_code/waypoints/output_theWaypoints.npz" 
    
    if os.path.exists(REFERENCE_TRACK) and os.path.exists(EDITABLE_PATH_1) and os.path.exists(EDITABLE_PATH_2):
        print(f"Loading {REFERENCE_TRACK} as boundaries...")
        print("Loading editable paths...")
        editor = TrackEditor(REFERENCE_TRACK, EDITABLE_PATH_1, EDITABLE_PATH_2, car_width=CAR_WIDTH, car_length=CAR_LENGTH, wall_margin=WALL_MARGIN)
        plt.show()
    else:
        print("Error: Could not find required .npz files.")
        print(f"Looking for:\n- {REFERENCE_TRACK}\n- {EDITABLE_PATH_1}\n- {EDITABLE_PATH_2}")
