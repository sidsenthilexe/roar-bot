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
        (745, 880, 5), 
        (1300, 1320, 11), 
        (1320, 1400, 2), 
        (1400, 1425, 7), 
        (1800, 1900, 9), 
        (2550, 2600, -1)
    ]

    @staticmethod
    def tune_target_speed(target_speed, waypoint):
        for s, e, f in Tuner.WAYPOINT_TO_TARGET_SPEED:
            if s <= waypoint <= e:
                return target_speed * f
        return target_speed * 44/35

    @staticmethod
    def tune_steer(steer, waypoint):
        if (490 <= waypoint < 505): return steer * 0.75
        if (510 <= waypoint <= 520): return max(steer * 2.0, 0)
        if (1855 <= waypoint <= 1900): return max(steer * 3.0, 0)
        if (830 <= waypoint <= 845): return max(steer * 0.9, 0)
        if (845 < waypoint < 860): return max(steer * 1.5, 0)
        if (860 <= waypoint <= 880): return steer * 0.4
        if (1320 <= waypoint <= 1340): return min(steer, 0.3)
        if (1425 <= waypoint <= 1450): return min(steer, 0.01)
        if (2550 <= waypoint <= 2600): return steer * 0.75
        if (2610 <= waypoint <= 2620): return steer * 0.5
        if (waypoint > 2620): return steer * 0.075 if steer < 0 else steer * 0.05
        return steer

    @staticmethod
    def tune_steer_lookahead(lookahead, waypoint):
        for s, e, a in Tuner.WAYPOINT_TO_STEER_LOOKAHEAD:
            if s <= waypoint <= e:
                return lookahead + a
        return lookahead

    @staticmethod
    def tune_inputs(wp, throttle, brake):
        if (2550 <= wp <= 2580): return (0.0, 1.0)
        if (1240 <= wp <= 1251): return (1.0, 0.0)
        return (throttle, brake)


    @staticmethod
    def tune_speed_lookahead(lookahead, waypoint):
        if (370 <= waypoint <= 410): return lookahead - 5
        if (605 <= waypoint <= 675): return lookahead - 20
        if (745 <= waypoint <= 870): return lookahead - 23
        if (2500 <= waypoint <= 2580): return lookahead - 7
        return lookahead
    
