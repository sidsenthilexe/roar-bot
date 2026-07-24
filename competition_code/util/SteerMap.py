import numpy as np
class SteerMap:

    @staticmethod
    def look_ahead_dist(velocity):
        return int(np.clip(0.6 * velocity - 3.0, 6.0, 25.0))


        if (velocity < 20):
            return 6
        elif (velocity < 35):
            return 12
        elif (velocity < 50):
            return 18
        else:
            return 25
        
