class Tuner:

    @staticmethod
    def tune_target_speed(target_speed, waypoint):
        if (waypoint < 450 or 745 <= waypoint <= 870 or 1200 <= waypoint <= 1450 or (waypoint >= 2550 and target_speed > 35)): return target_speed * 38/35
        elif (waypoint >= 2550): return target_speed 
        elif (450 <= waypoint <= 510): return min(target_speed, 34.9)
        return target_speed * 44/35

    def decide_steer_pid(vel):
        if (vel < 33): return 1.2
        return 1.35
    
    
    