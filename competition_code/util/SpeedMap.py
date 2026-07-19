class SpeedMap:
    
    @staticmethod
    def get_target(curvature):
        if (curvature < 0.0005):
            return 75
        elif (curvature < 0.001):
            return 65
        elif (curvature < 0.0025):
            return 55
        elif (curvature < 0.006):
            return 45
        elif (curvature < 0.01):
            return 30
        elif (curvature < 0.02):
            return 20
        else:
            return 10
