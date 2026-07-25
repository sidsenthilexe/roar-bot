import numpy as np
from util.MathUtil import MathUtil
from util.SteerMap import SteerMap

class SteerController:

    @staticmethod
    def get_steer_control(velocity, vehicle, loc, rot):
        steer_look_ahead = SteerMap.look_ahead_dist(velocity)
        target_waypoint = vehicle.maneuverable_waypoints[(vehicle.current_waypoint_idx + steer_look_ahead) % len(vehicle.maneuverable_waypoints)]
        vector_to_waypoint = (target_waypoint.location - loc)[:2]
        heading_to_waypoint = np.arctan2(vector_to_waypoint[1],vector_to_waypoint[0])
        delta_heading = MathUtil.normalize_rad(heading_to_waypoint - rot[2])
        gain = 12 + 0.05 * velocity
        steer_control = (-gain / (velocity ** 0.4) * delta_heading / np.pi) if velocity > 1e-2 else -np.sign(delta_heading)
        steer_control = np.clip(steer_control, -1.0, 1.0)
        return steer_control

    def get_target_heading(velocity, vehicle, loc, rot):
        steer_look_ahead = SteerMap.look_ahead_dist(velocity)
        target_waypoint = vehicle.maneuverable_waypoints[(vehicle.current_waypoint_idx + steer_look_ahead) % len(vehicle.maneuverable_waypoints)]
        vector_to_waypoint = (target_waypoint.location - loc)[:2]
        return MathUtil.normalize_rad(np.arctan2(vector_to_waypoint[1],vector_to_waypoint[0]))



