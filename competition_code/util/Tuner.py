class Tuner:

    @staticmethod
    def tune_target_speed(target_speed, waypoint):
        if (target_speed > 35):
            if (waypoint <= 520 or 745 <= waypoint <= 870 or 1100 <= waypoint <= 1450 or waypoint >= 2550):
                return target_speed * 38/35
            else: return target_speed * 40/35
        return target_speed