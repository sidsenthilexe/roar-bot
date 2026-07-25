import numpy as np

class MathUtil:

    @staticmethod
    def normalize_rad(rad : float):
        return (rad + np.pi) % (2 * np.pi) - np.pi

    def normalize_continuous_target_rads(current_heading: float, target_heading: float) -> float:
        diff = target_heading - current_heading

        adjusted_target = target_heading

        while diff > np.pi:
            adjusted_target -= 2 * np.pi
            diff = adjusted_target - current_heading
        while diff < -np.pi:
            adjusted_target += 2 * np.pi
            diff = adjusted_target - current_heading

        return adjusted_target

    @staticmethod
    def input_modulus(input, min_input, max_input):
        modulus = max_input - min_input

        num_max = int((input-min_input)/modulus)

        input -= num_max * modulus

        num_min = int((input-max_input)/modulus)
        input -= num_min * modulus

        return input
    
    @staticmethod
    def clamp_inputs(throttle, brake, steer):
        steer_scalar = 1.0 - abs(steer)
        clamped_throttle = throttle * steer_scalar
        clamped_brake = brake * steer_scalar

        return max(0.0, min(1.0, clamped_throttle)), max(0.0, min(1.0, clamped_brake)), steer

