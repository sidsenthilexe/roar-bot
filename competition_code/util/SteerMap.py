import numpy as np

class SteerMap:

    @staticmethod
    def look_ahead_dist(v):
        if (v < 20):
            return 6
        elif (v < 35):
            return 12
        elif (v < 50):
            return 18
        else:
            return 25

    
