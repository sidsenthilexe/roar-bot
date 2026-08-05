import numpy as np
from util.MathUtil import MathUtil
from util.Tuner import Tuner

class Calculator:

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
        speed_wp = [vehicle.maneuverable_waypoints[(vehicle.current_waypoint_idx + spd_look_ahead) % len(vehicle.maneuverable_waypoints)], vehicle.maneuverable_waypoints[(vehicle.current_waypoint_idx + spd_look_ahead+20) % len(vehicle.maneuverable_waypoints)]]
        curvature = Calculator.curvature(current_waypoint, speed_wp[0], speed_wp[1])
        return np.clip(7.62945* ((curvature)**-0.300321), 0.0, 100.0)

    @staticmethod
    def vector_to_waypoint(wp_1, wp_2):
        return (wp_1.location - wp_2.location)[:2]
    
    @staticmethod
    def hdg(vector):
        return np.arctan2(vector[1], vector[0])
        
    @staticmethod
    def dist(wp_1, wp_2):
        return np.linalg.norm((wp_1.location - wp_2.location)[:2])
        
    @staticmethod
    def curvature(wp_0, wp_1, wp_2):
        vector_wp_1 = Calculator.vector_to_waypoint(wp_1, wp_0)
        vector_wp_2 = Calculator.vector_to_waypoint(wp_2, wp_1)
        hdg_wp_1 = Calculator.hdg(vector_wp_1)
        hdg_wp_2 = Calculator.hdg(vector_wp_2)
        first_element_dist = Calculator.dist(wp_1, wp_0)
        second_element_dist = Calculator.dist(wp_1, wp_2)
        heading_diff = MathUtil.normalize_rad(hdg_wp_2 - hdg_wp_1)
        curvature = abs(heading_diff) / (first_element_dist + second_element_dist)
        return curvature
