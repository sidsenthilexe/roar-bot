import numpy as np
from util.MathUtil import MathUtil

class SteerController:

    @staticmethod
    def get_target_angle(target, car_loc, car_rot, wheelbase):
        dx = target.location[0] - car_loc[0]
        dy = target.location[1] - car_loc[1]
        actual_look_ahead = max(1.0, np.hypot(dx, dy))
        angle_diff = MathUtil.normalize_rad(np.arctan2(dy, dx) - car_rot[2])
        steer_angle = np.arctan(2 * wheelbase * np.sin(angle_diff) / actual_look_ahead)
        return -steer_angle


