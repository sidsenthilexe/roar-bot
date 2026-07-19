import numpy as np

class WaypointCalculator:

    @classmethod
    def vector_to_waypoint(wp_1, wp_2):
        return (wp_1.location - wp_2.location)[:2]

    @classmethod
    def hdg(vector):
        return np.arctan2(vector[1], vector[0])
    
    @classmethod
    def dist(wp_1, wp_2):
        return np.linalg.norm((wp_1.location - wp_2.location)[:2])
