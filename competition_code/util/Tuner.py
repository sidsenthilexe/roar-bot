import numpy as np

class Tuner:

    WAYPOINT_TO_TARGET_SPEED = [
        (0, 300, 10/7), 
        (300, 510, 38/35), 
        (600, 710, 19/14), 
        (745, 870, 19/14), 
        (1300, 1325, 10/7), 
        (1400, 1425, 10/7), 
        (1750, 2000, 11/7), 
        (2550, np.inf, 38/35)
    ]

    WAYPOINT_TO_STEER_LOOKAHEAD = [
        (450, 490, 4), 
        (660, 700, 4), 
        (745, 838, 4), 
        (1300, 1325, 7), 
        (1400, 1425, 7), 
        (1800, 1900, 9), 
        (2550, 2600, 2)
    ]

    @staticmethod
    def tune_target_speed(target_speed, waypoint):
        for s, e, f in Tuner.WAYPOINT_TO_TARGET_SPEED:
            if s <= waypoint <= e:
                return target_speed * f
        return target_speed * 44/35

    @staticmethod
    def tune_steer(steer, waypoint):
        if (470 <= waypoint <= 530): steer * 3.5
        if (1855 <= waypoint <= 1900): return max(steer * 3.0, 0)
        if (830 <= waypoint < 860): return max(steer * 1.5, 0)
        if (860 <= waypoint <= 880): return steer * 0.4
        return steer

    @staticmethod
    def tune_steer_lookahead(lookahead, waypoint):
        for s, e, a in Tuner.WAYPOINT_TO_STEER_LOOKAHEAD:
            if s <= waypoint <= e:
                return lookahead + a
        return lookahead

    @staticmethod
    def tune_speed_lookahead(lookahead, waypoint):
        if (370 <= waypoint <= 410): return lookahead - 5
        if (605 <= waypoint <= 675): return lookahead - 20
        if (745 <= waypoint <= 870): return lookahead - 23
        return lookahead
    