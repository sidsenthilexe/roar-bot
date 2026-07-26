import numpy as np

class SteerMap:

    @staticmethod
    def look_ahead_dist(velocity):
        return np.clip(int(0.4 * velocity - 2), 6, 26)
        if (velocity < 20):
            return 6
        elif (velocity < 35):
            return 12
        elif (velocity < 50):
            return 18
        else:
            return 25
        
