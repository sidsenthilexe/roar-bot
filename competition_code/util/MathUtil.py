class MathUtil:

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
        active_pedal = throttle if throttle > 0.0 else brake

        total = abs(steer) + active_pedal
        if total > 1.0:
            active_pedal = 1.0-abs(steer)
            if throttle > 0:
                throttle = active_pedal
            else:
                brake = active_pedal

        return throttle, brake, steer

