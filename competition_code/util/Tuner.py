import numpy as np

class Tuner:

    @staticmethod
    def tune_target_speed(target_speed, waypoint):
        if (745 <= waypoint <= 870): return target_speed * 40/35
        if (waypoint <= 510 or waypoint >= 2550): return target_speed * 38/35
        return target_speed * 44/35

    @staticmethod
    def tune_steer_kP(target_speed):
        if (target_speed < 35): return 1.2
        return 1.3

    @staticmethod
    def tune_steer(steer, waypoint):
        if (840 <= waypoint <= 860): return max(steer * 2.0, 0)
        return steer

    @staticmethod
    def tune_steer_lookahead(lookahead, waypoint):
        if (745 <= waypoint < 838): return lookahead + 4
        if (1300 <= waypoint <= 1325 or 1400 <= waypoint <= 1425): return lookahead + 7
        elif (450 <= waypoint < 490 or 2550 <= waypoint <= 2600): return lookahead + 2
        return lookahead  
    