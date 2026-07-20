import numpy as np

class WaypointCalculator:

    @staticmethod
    def normalize_rad(rad : float):
        return (rad + np.pi) % (2 * np.pi) - np.pi

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
        vector_wp_1 = WaypointCalculator.vector_to_waypoint(wp_1, wp_0)
        vector_wp_2 = WaypointCalculator.vector_to_waypoint(wp_2, wp_1)
        hdg_wp_1 = WaypointCalculator.hdg(vector_wp_1)
        hdg_wp_2 = WaypointCalculator.hdg(vector_wp_2)
        first_element_dist = WaypointCalculator.dist(wp_1, wp_0)
        second_element_dist = WaypointCalculator.dist(wp_1, wp_2)
        heading_diff = WaypointCalculator.normalize_rad(hdg_wp_2 - hdg_wp_1)
        curvature = abs(heading_diff) / (first_element_dist + second_element_dist)
        return curvature

    