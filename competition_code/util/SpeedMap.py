import numpy as np
from util.WaypointCalculator import WaypointCalculator

class SpeedMap:
    
    @staticmethod
    def get_target_speed(velocity, vehicle):
        waypoints = vehicle.maneuverable_waypoints
        idx = vehicle.current_waypoint_idx
        n = len(waypoints)
        spd_look_ahead = np.clip(int(velocity * 0.4), 15, 35)
        max_c = 1e-5
        for i in range(spd_look_ahead):
            w_0 = waypoints[(idx + i) % n]
            w_1 = waypoints[(idx + i + 4) % n]
            w_2 = waypoints[(idx + i + 8) % n]
            curvature = WaypointCalculator.curvature(w_0, w_1, w_2)
            if curvature > max_c:
                max_c = curvature
        print(f"Curvature: {max_c}")
        return np.clip(4.5 * (max_c ** -0.45), 0.0, 100.0)

    #spd_look_ahead = np.clip(int(velocity * 0.4), 15, 35)
            #radii = [vehicle.radii_data[(vehicle.current_waypoint_idx + i) % len(vehicle.radii_data)] for i in range(spd_look_ahead)]
            #radius = np.percentile(radii, 20)
            #return np.clip(12 * (radius ** 0.28), 0, 100)

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
