import numpy as np
from util.MathUtil import MathUtil

class SteerController:

    @staticmethod
    def get_target_heading(velocity, vehicle, loc):
        steer_look_ahead = SteerController.look_ahead_dist(velocity)
        target_waypoint = vehicle.maneuverable_waypoints[(vehicle.current_waypoint_idx + steer_look_ahead) % len(vehicle.maneuverable_waypoints)]
        vector_to_waypoint = (target_waypoint.location - loc)[:2]
        return MathUtil.normalize_rad(np.arctan2(vector_to_waypoint[1],vector_to_waypoint[0]))

    @staticmethod
    def look_ahead_dist(velocity):
        return np.clip(int(0.4 * velocity - 2), 6, 26)



