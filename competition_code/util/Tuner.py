import numpy as np

class Tuner:

    @staticmethod
    def tune_target_speed(target_speed):
        if (target_speed > 35):
            return target_speed + 5
        return target_speed
