import numpy as np

class SpeedMap:
    
    @staticmethod
    def get_target(x):
        return np.clip(7.62945* ((x*0.6)**-0.300321), 0.0, 100.0)

    # @staticmethod
    # def get_target_old(curvature):
    #     if (curvature < 0.00015):
    #         return 100
    #     if (curvature < 0.0003):
    #         return 85
    #     elif (curvature < 0.0005):
    #         return 75
    #     elif (curvature < 0.0025):
    #         return 50
    #     elif (curvature < 0.006):
    #         return 45
    #     elif (curvature < 0.01):
    #         return 30
    #     elif (curvature < 0.02):
    #         return 20
    #     else:
    #         return 10
