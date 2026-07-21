import numpy as np
from util.MathUtil import MathUtil

class SteerController:

    @staticmethod
    def get_target_angle(target, car_loc, car_rot, wheelbase):
        dx = target.location[0] - car_loc[0]
        dy = target.location[1] - car_loc[1]
        actual_look_ahead = max(1e-6, np.hypot(dx, dy))
        angle_diff = MathUtil.normalize_rad(np.arctan2(dy, dx) - car_rot[2])
        curvature = 2 * np.sin(angle_diff) / actual_look_ahead
        steer_angle = np.arctan(wheelbase * curvature)
        return -steer_angle

