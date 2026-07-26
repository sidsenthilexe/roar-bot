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


    # @staticmethod
    # def get_target_old(curvature):
    #     if (curvature < 0.00015):
    #         return 100
    #     if (curvature < 0.0003):
    #         return 85
    #     elif (curvature < 0.0005):
    #         return 75
    #     elif (curvature < 0.0025):
    #         return 50
    #     elif (curvature < 0.006):
    #         return 45
    #     elif (curvature < 0.01):
    #         return 30
    #     elif (curvature < 0.02):
    #         return 20
    #     else:
    #         return 10
