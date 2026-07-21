import numpy as np
from util.MathUtil import MathUtil

class SteerController:

    @staticmethod
    def get_target_angle(target, car_loc, car_rot, vehicle):
        wheelbase = SteerController.get_vehicle_wheelbase(vehicle)
        dx = target.location[0] - car_loc[0]
        dy = target.location[1] - car_loc[1]
        actual_look_ahead = max(1e-6, np.hypot(dx, dy))
        angle_diff = MathUtil.normalize_rad(np.arctan2(dy, dx) - car_rot[2])
        curvature = 2 * np.sin(angle_diff) / actual_look_ahead
        steer_angle = np.arctan(wheelbase * curvature)
        return -steer_angle

    @staticmethod
    def get_vehicle_wheelbase(vehicle):
        wheels = vehicle.get_physics_control().wheels
        front = (wheels[0].position.x + wheels[1].position.x) / 200
        back = (wheels[2].position.x + wheels[3].position.x) / 200
        return abs(front - back)