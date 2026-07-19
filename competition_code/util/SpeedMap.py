class SpeedMap:
    
    @staticmethod
    def get_target(curvature):
        if (curvature < 0.0005):
            return 60
        elif (curvature < 0.0025):
            return 58
        elif (curvature < 0.0055):
            return 45
        elif (curvature < 0.0075):
            return 40
        elif (curvature < 0.0105):
            return 30
        elif (curvature < 0.015):
            return 22
        elif (curvature < 0.02):
            return 20
        else:
            return 10
