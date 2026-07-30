import numpy as np
from util.WaypointCalculator import WaypointCalculator

class SpeedMap:
    
    @staticmethod
    def get_target_speed(velocity, vehicle):
        current_waypoint = vehicle.maneuverable_waypoints[vehicle.current_waypoint_idx]
        spd_look_ahead = np.clip(int(velocity), 33, 53)
        speed_wp = [vehicle.maneuverable_waypoints[(vehicle.current_waypoint_idx + spd_look_ahead) % len(vehicle.maneuverable_waypoints)], vehicle.maneuverable_waypoints[(vehicle.current_waypoint_idx + spd_look_ahead+20) % len(vehicle.maneuverable_waypoints)]]
        curvature = WaypointCalculator.curvature(current_waypoint, speed_wp[0], speed_wp[1])
        return np.clip(7.62945* ((curvature)**-0.300321), 0.0, 100.0)
