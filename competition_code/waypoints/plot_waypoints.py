import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import os

# ==========================================
# CONFIGURATION
# ==========================================
CAR_WIDTH = 2.1634500027          # Width of the car in meters (editable)
CAR_LENGTH = 4.7917795181         # Length of the car in meters (editable)
WALL_MARGIN = 1.0               # Extra distance to maintain from track walls in meters (editable)
MIN_WAYPOINT_DIST = 0.7          # Minimum allowed distance between consecutive waypoints in meters
# ==========================================

class TrackEditor:
    def __init__(self, reference_filepath, target_filepath, car_width=CAR_WIDTH, car_length=CAR_LENGTH, wall_margin=WALL_MARGIN, min_dist=MIN_WAYPOINT_DIST):
        self.ref_filepath = reference_filepath
        self.target_filepath = target_filepath
        self.filename = os.path.basename(target_filepath)
        self.car_width = car_width
        self.car_length = car_length
        self.wall_margin = wall_margin
        self.min_dist = min_dist
        
        # Edit mode: 'inner' (middle points) or 'ends' (start/end points)
        self.edit_mode = 'inner'
        self.show_car_boxes = False  # Toggle state for 2D car body boxes
        self.current_mouse_event = None  # Track mouse position for keypress actions
        
        # 1. Load Reference Data (Monza Track Bounds)
        self.ref_x, self.ref_y, self.ref_widths, *_ = self._load_npz(reference_filepath)
        if self.ref_widths is None:
            raise ValueError(f"Reference file '{reference_filepath}' must contain 'lane_widths' to draw track bounds.")
            
        # 2. Load Target Data (Editable Waypoints)
        target_data = self._load_npz(target_filepath, keep_original=True)
        self.x, self.y, self.widths = target_data[0], target_data[1], target_data[2]
        self.original_dict = target_data[3]
        self.load_mode = target_data[4]

        # 3. Setup Figure
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.fig.canvas.manager.set_window_title(f"Racing Line Editor - {self.filename}")
        
        # 4. Draw Static Reference Track (Monza Walls)
        self._plot_reference_track()
        
        # 5. Draw Editable Target Track
        # Car Widths (Green lines, thicker width)
        car_widths_array = np.full_like(self.x, self.car_width)
        car_segments = self._calculate_perpendicular_segments(self.x, self.y, car_widths_array)
        self.car_lines = LineCollection(car_segments, colors='green', linewidths=2.0, alpha=0.8, zorder=3)
        self.ax.add_collection(self.car_lines)

        # Car 2D Body Boxes (Toggleable display)
        car_box_segments = self._calculate_car_boxes(self.x, self.y)
        self.car_boxes = LineCollection(car_box_segments, colors='magenta', linewidths=1.0, alpha=0.6, zorder=3.5)
        self.car_boxes.set_visible(self.show_car_boxes)
        self.ax.add_collection(self.car_boxes)

        # Main Racing Line Path
        self.line, = self.ax.plot(self.x, self.y, 'b-', linewidth=1.5, zorder=4, label="Racing Line")
        
        # Waypoint Scatter
        self.scatter = self.ax.scatter([], [], zorder=5, edgecolors='black', linewidths=0.5)
        self._update_scatter_points()
        
        # Plot styling
        self.ax.axis('equal')
        self.ax.grid(True, linestyle='--', alpha=0.4)
        self.ax.set_xlabel("X Coordinate (m)")
        self.ax.set_ylabel("Y Coordinate (m)")
        
        # Initialize UI title
        self._update_title()
        
        # 6. State Variables for Dragging and Undo
        self._ind = None
        self._dragging = False
        self.undo_stack = []

        # 7. Connect Matplotlib Events
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def _update_scatter_points(self):
        """Re-evaluates waypoint colors and sizes based on current array length."""
        colors = ['red'] * len(self.x)
        if len(self.x) > 0:
            colors[0] = 'green'
            colors[-1] = 'orange'
        
        sizes = [15] * len(self.x)
        if len(self.x) > 0:
            sizes[0] = sizes[-1] = 50
            
        self.scatter.set_offsets(np.column_stack([self.x, self.y]))
        self.scatter.set_color(colors)
        self.scatter.set_sizes(sizes)

    def _calculate_lap_length(self):
        """Calculates total lap length in meters."""
        if len(self.x) < 2:
            return 0.0
        return float(np.sum(np.hypot(np.diff(self.x), np.diff(self.y))))

    def _update_title(self):
        """Updates graph title with current editing mode, total points, and total lap length."""
        mode_str = "Middle Points" if self.edit_mode == 'inner' else "Start & End Points"
        lap_len = self._calculate_lap_length()
        box_str = "ON" if self.show_car_boxes else "OFF"
        
        title_text = (
            f"Editing: {self.filename} | Target: {mode_str} | Waypoints: {len(self.x)} | Lap Distance: {lap_len:.2f} m\n"
            f"'t'=Toggle Edit | 'd'=Delete | 'e'=Clean Close (<{self.min_dist}m) | 'b'=Car Boxes ({box_str}) | 's'=Save | 'z'=Undo | 'o'/'p'=Optimize"
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
        """Generates 2D closed polygon boxes representing the full length and width of the car."""
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
        """Refreshes plot lines, car shapes, scatter markers, and header."""
        self.line.set_data(self.x, self.y)
        self._update_scatter_points()
        
        car_widths_array = np.full_like(self.x, self.car_width)
        self.car_lines.set_segments(self._calculate_perpendicular_segments(self.x, self.y, car_widths_array))
        
        if self.show_car_boxes:
            self.car_boxes.set_segments(self._calculate_car_boxes(self.x, self.y))
            
        self._update_title()

    def clean_close_waypoints(self, min_distance=None):
        """
        Removes consecutive waypoints that are closer than min_distance meters.
        Preserves the start and end waypoints.
        """
        if min_distance is None:
            min_distance = self.min_dist

        if len(self.x) <= 3:
            return

        keep_indices = [0]
        for i in range(1, len(self.x) - 1):
            last_kept_idx = keep_indices[-1]
            dist = np.hypot(self.x[i] - self.x[last_kept_idx], self.y[i] - self.y[last_kept_idx])
            if dist >= min_distance:
                keep_indices.append(i)

        # Always preserve the end point
        if keep_indices[-1] != len(self.x) - 1:
            dist_to_last = np.hypot(self.x[-1] - self.x[keep_indices[-1]], self.y[-1] - self.y[keep_indices[-1]])
            if dist_to_last < min_distance and len(keep_indices) > 1:
                keep_indices.pop()  # Drop second to last if too close to end point
            keep_indices.append(len(self.x) - 1)

        removed_count = len(self.x) - len(keep_indices)
        if removed_count > 0:
            self.x = self.x[keep_indices]
            self.y = self.y[keep_indices]
            print(f"Cleaned up {removed_count} waypoints closer than {min_distance}m!")
            self._refresh_visuals()

    def get_closest_point(self, event, ignore_mode=False):
        """Finds the waypoint index closest to the event cursor."""
        if event is None or event.xdata is None or event.ydata is None: 
            return None
            
        xlim = self.ax.get_xlim()
        threshold = (xlim[1] - xlim[0]) * 0.02
        
        if ignore_mode:
            distances = np.hypot(self.x - event.xdata, self.y - event.ydata)
            closest_idx = np.argmin(distances)
            if distances[closest_idx] < threshold:
                return closest_idx
            return None

        if self.edit_mode == 'inner':
            valid_x, valid_y = self.x[1:-1], self.y[1:-1]
            if len(valid_x) == 0:
                return None
                
            distances = np.hypot(valid_x - event.xdata, valid_y - event.ydata)
            closest_valid_idx = np.argmin(distances)
            
            if distances[closest_valid_idx] < threshold:
                return closest_valid_idx + 1
                
        elif self.edit_mode == 'ends':
            ends_x = np.array([self.x[0], self.x[-1]])
            ends_y = np.array([self.y[0], self.y[-1]])
            
            distances = np.hypot(ends_x - event.xdata, ends_y - event.ydata)
            closest_valid_idx = np.argmin(distances)
            
            if distances[closest_valid_idx] < threshold:
                return 0 if closest_valid_idx == 0 else len(self.x) - 1
                
        return None

    def delete_waypoint(self, idx):
        """Deletes a waypoint at index idx with safety checks and undo support."""
        if idx is None or len(self.x) <= 3:
            return

        self.undo_stack.append((self.x.copy(), self.y.copy()))
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

        self.x = np.delete(self.x, idx)
        self.y = np.delete(self.y, idx)
        
        print(f"Deleted waypoint {idx}. ({len(self.x)} waypoints remaining)")
        self._refresh_visuals()

    def on_press(self, event):
        if event.inaxes != self.ax or event.button != 1: 
            return
        
        self._ind = self.get_closest_point(event)
        if self._ind is not None:
            self.undo_stack.append((self.x.copy(), self.y.copy()))
            if len(self.undo_stack) > 50:
                self.undo_stack.pop(0)
            self._dragging = True

    def on_motion(self, event):
        self.current_mouse_event = event
        if not self._dragging or self._ind is None or event.inaxes != self.ax: 
            return
        
        self.x[self._ind] = event.xdata
        self.y[self._ind] = event.ydata
        self._refresh_visuals()

    def on_release(self, event):
        self._dragging = False
        self._ind = None

    def on_key(self, event):
        if event.key == 's':
            self.save_data()
        elif event.key == 'e':
            self.undo_stack.append((self.x.copy(), self.y.copy()))
            self.clean_close_waypoints()
        elif event.key in ['d', 'delete', 'backspace']:
            target_idx = self.get_closest_point(self.current_mouse_event, ignore_mode=True)
            if target_idx is not None:
                self.delete_waypoint(target_idx)
            else:
                print("Hover over a waypoint to delete it.")
        elif event.key == 'z' or event.key == 'ctrl+z':
            self.undo()
        elif event.key == 't':
            self.edit_mode = 'ends' if self.edit_mode == 'inner' else 'inner'
            self._update_title()
        elif event.key == 'b':
            self.show_car_boxes = not self.show_car_boxes
            self.car_boxes.set_visible(self.show_car_boxes)
            self._refresh_visuals()
        elif event.key == 'o':
            self.optimize_racing_line(fix_endpoints=False)
        elif event.key == 'p':
            self.optimize_racing_line(fix_endpoints=True)

    def optimize_racing_line(self, iterations=100, alpha=0.6, fix_endpoints=False):
        """Geometrically optimizes the racing line and removes stacked waypoints."""
        mode_msg = "locking endpoints" if fix_endpoints else "including endpoints"
        print(f"Optimizing racing line ({mode_msg})...")
        
        self.undo_stack.append((self.x.copy(), self.y.copy()))
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

        new_x = self.x.copy()
        new_y = self.y.copy()

        start_idx = 1 if fix_endpoints else 0
        end_idx = len(self.x) - 1 if fix_endpoints else len(self.x)

        for _ in range(iterations):
            temp_x = new_x.copy()
            temp_y = new_y.copy()
            
            for i in range(start_idx, end_idx):
                prev_i = max(0, i - 1)
                next_i = min(len(self.x) - 1, i + 1)
                
                target_x = (temp_x[prev_i] + temp_x[next_i]) / 2.0
                target_y = (temp_y[prev_i] + temp_y[next_i]) / 2.0

                new_x[i] = temp_x[i] + alpha * (target_x - temp_x[i])
                new_y[i] = temp_y[i] + alpha * (target_y - temp_y[i])

                dists = np.hypot(self.ref_x - new_x[i], self.ref_y - new_y[i])
                closest_idx = np.argmin(dists)

                max_dist = (self.ref_widths[closest_idx] / 2.0) - (self.car_width / 2.0) - self.wall_margin
                max_dist = max(0.0, max_dist)

                vec_x = new_x[i] - self.ref_x[closest_idx]
                vec_y = new_y[i] - self.ref_y[closest_idx]
                dist_from_center = np.hypot(vec_x, vec_y)

                if dist_from_center > max_dist:
                    vec_x /= dist_from_center
                    vec_y /= dist_from_center
                    new_x[i] = self.ref_x[closest_idx] + vec_x * max_dist
                    new_y[i] = self.ref_y[closest_idx] + vec_y * max_dist

        self.x = new_x
        self.y = new_y
        
        # Perform automatic cleanup of waypoints closer than MIN_WAYPOINT_DIST
        self.clean_close_waypoints()
        self._refresh_visuals()
        print("Optimization complete!")

    def undo(self):
        if not self.undo_stack:
            return
            
        self.x, self.y = self.undo_stack.pop()
        self._refresh_visuals()
        print(f"Undo successful. ({len(self.undo_stack)} steps remaining)")

    def save_data(self):
        new_filename = f"output_{self.filename}"
        save_path = os.path.join(os.path.dirname(self.target_filepath), new_filename)
        
        save_dict = self.original_dict.copy()
        num_points = len(self.x)

        if 'locations' in save_dict:
            orig_shape = save_dict['locations'].shape
            if orig_shape[1] == 3:
                old_z = save_dict['locations'][:, 2] if len(save_dict['locations']) == num_points else np.zeros(num_points)
                save_dict['locations'] = np.column_stack([self.x, self.y, old_z])
            else:
                save_dict['locations'] = np.column_stack([self.x, self.y])
        elif self.load_mode == 'xy':
            save_dict['x'] = self.x
            save_dict['y'] = self.y
        elif self.load_mode == 'waypoints':
            save_dict['waypoints'] = np.column_stack([self.x, self.y])

        if 'rotations' in save_dict:
            dx = np.gradient(self.x)
            dy = np.gradient(self.y)
            yaws = np.arctan2(dy, dx)
            
            rot_shape = save_dict['rotations'].shape
            if len(rot_shape) == 1 or (len(rot_shape) == 2 and rot_shape[1] == 1):
                save_dict['rotations'] = yaws
            elif len(rot_shape) == 2 and rot_shape[1] >= 3:
                new_rots = np.zeros((num_points, rot_shape[1]))
                new_rots[:, -1] = yaws
                save_dict['rotations'] = new_rots

        if 'lane_widths' in save_dict:
            save_dict['lane_widths'] = np.full(num_points, self.car_width)

        np.savez(save_path, **save_dict)
        print(f"Saved modified file to: {save_path}")
        print(f"Exported fields: {list(save_dict.keys())}")
        
        self.ax.set_title(f"SAVED TO:\n{new_filename}", color='green', fontweight='bold', fontsize=12)
        self.fig.canvas.draw_idle()
        
        timer = self.fig.canvas.new_timer(interval=2000)
        timer.add_callback(self._update_title)
        timer.start()


if __name__ == "__main__":
    REFERENCE_TRACK = "Monza.npz"
    EDITABLE_PATH = "edited_waypointsPrimary.npz"
    
    if os.path.exists(REFERENCE_TRACK) and os.path.exists(EDITABLE_PATH):
        print(f"Loading {REFERENCE_TRACK} as boundaries...")
        print(f"Loading {EDITABLE_PATH} as editable racing line...")
        editor = TrackEditor(REFERENCE_TRACK, EDITABLE_PATH, car_width=CAR_WIDTH, car_length=CAR_LENGTH, wall_margin=WALL_MARGIN)
        plt.show()
    else:
        print("Error: Could not find one or both of the required .npz files.")
        print(f"Looking for: '{REFERENCE_TRACK}' and '{EDITABLE_PATH}'")