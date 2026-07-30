class SteerMap:

    @staticmethod
    def look_ahead_dist(velocity):
        if (velocity < 20):
            return 6
        elif (velocity < 35):
            return 12
        elif (velocity < 50):
            return 18
        else:
            return 25
        
