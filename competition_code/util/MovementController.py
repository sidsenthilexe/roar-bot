import numpy as np
from util.WaypointCalculator import WaypointCalculator
from util.MathUtil import MathUtil
from util.Tuner import Tuner

class MovementController:

    @staticmethod
    def get_target_heading(velocity, vehicle, loc):
        steer_look_ahead = np.clip(int(0.4 * velocity - 2), 6, 26)
        steer_look_ahead = Tuner.tune_steer_lookahead(steer_look_ahead, vehicle.current_waypoint_idx)
        target_waypoint = vehicle.maneuverable_waypoints[(vehicle.current_waypoint_idx + steer_look_ahead) % len(vehicle.maneuverable_waypoints)]
        vector_to_waypoint = (target_waypoint.location - loc)[:2]
        return MathUtil.normalize_rad(np.arctan2(vector_to_waypoint[1],vector_to_waypoint[0]))

    @staticmethod
    def get_target_speed(velocity, vehicle):
        current_waypoint = vehicle.maneuverable_waypoints[vehicle.current_waypoint_idx]
        spd_look_ahead = np.clip(int(velocity), 33, 53)
        spd_look_ahead = Tuner.tune_speed_lookahead(spd_look_ahead, vehicle.current_waypoint_idx)
        speed_wp = [vehicle.maneuverable_waypoints[(vehicle.current_waypoint_idx + spd_look_ahead) % len(vehicle.maneuverable_waypoints)], vehicle.maneuverable_waypoints[(vehicle.current_waypoint_idx + spd_look_ahead+20) % len(vehicle.maneuverable_waypoints)]]
        curvature = WaypointCalculator.curvature(current_waypoint, speed_wp[0], speed_wp[1])
        return np.clip(7.62945* ((curvature)**-0.300321), 0.0, 100.0)
