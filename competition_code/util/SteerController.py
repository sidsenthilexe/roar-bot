import numpy as np
from util.MathUtil import MathUtil
from util.Tuner import Tuner

class SteerController:

    @staticmethod
    def get_target_heading(velocity, vehicle, loc):
        steer_look_ahead = np.clip(int(0.4 * velocity - 2), 6, 26)
        steer_look_ahead = Tuner.tune_steer_lookahead(steer_look_ahead, vehicle.current_waypoint_idx)
        target_waypoint = vehicle.maneuverable_waypoints[(vehicle.current_waypoint_idx + steer_look_ahead) % len(vehicle.maneuverable_waypoints)]
        vector_to_waypoint = (target_waypoint.location - loc)[:2]
        return MathUtil.normalize_rad(np.arctan2(vector_to_waypoint[1],vector_to_waypoint[0]))
