import numpy as np

class SteerMap:

    @staticmethod
    def look_ahead_dist(v):
        return int(np.clip(0.4 * v - 2, 6, 25))

    @staticmethod
    def look_ahead_dist2(v):
        if (v < 20):
            return 6
        elif (v < 35):
            return 12
        elif (v < 50):
            return 18
        else:
            return 25

    #@staticmethod
    #def look_ahead_dist(v):
    #    return np.clip(int(0.1 * v + 2), 4, 20)
    
