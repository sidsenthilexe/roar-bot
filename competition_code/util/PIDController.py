# PIDController based on WPILib

from util.MathUtil import MathUtil
import numpy as np
import math


class PIDController:

    def __init__(self, kp, ki, kd, period = 0.02):
        if (type(kp) != int and type(kp) != float):
            raise TypeError("Kp must be int or float") 
        if (type(ki) != int and type(ki) != float):
            raise TypeError("Ki must be int or float")
        if (type(kd) != int and type(kd) != float):
            raise TypeError("Kd must be int or float")
        
        if (kp < 0.0):
            raise ValueError("Kp must be non-negative")
        if (ki < 0.0):
            raise ValueError("Ki must be non-negative")
        if (kd < 0.0):
            raise ValueError("Kd must be non-negative")

        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.period = period

        self.i_zone = float('inf')
        self.max_integral = 1.0
        self.min_integral = -1.0

        self.max_input = 0.0
        self.min_input = 0.0

        self.continuous = False

        self.error = 0.0
        self.error_derivative = 0.0
        
        self.prev_error = 0.0
        self.total_error = 0.0
        
        self.error_tolerance = 0.05
        self.error_derivative_tolerance = float('inf')

        self.setpoint = 0.0
        self.measurement = 0.0

        self.have_measurement = False
        self.have_setpoint = False

    def set_pid(self, kp, ki, kd):
        if (type(kp) != int and type(kp) != float):
            raise TypeError("Kp must be int or float") 
        if (type(ki) != int and type(ki) != float):
            raise TypeError("Ki must be int or float")
        if (type(kd) != int and type(kd) != float):
            raise TypeError("Kd must be int or float")
        
        if (kp < 0.0):
            raise ValueError("Kp must be non-negative")
        if (ki < 0.0):
            raise ValueError("Ki must be non-negative")
        if (kd < 0.0):
            raise ValueError("Kd must be non-negative")

        self.kp = kp
        self.ki = ki
        self.kd = kd
    
    def set_iZone(self, iZone):
        if (type(iZone) != int and type(iZone) != float):
            raise TypeError("IZone must be int or float")
        if (iZone < 0):
            raise ValueError("IZone must be non-negative")
        self.i_zone = iZone

    def set_setpoint(self, setpoint):
        self.setpoint = setpoint
        self.have_setpoint = True

        self.error = self.setpoint - self.measurement

        self.error_derivative = (self.error - self.prev_error) / self.period

    
    def at_setpoint(self):
        return (self.have_measurement 
                and self.have_setpoint 
                and abs(self.error) < self.error_tolerance 
                and abs(self.error_derivative) < self.error_derivative_tolerance)
    
    def enable_continuous_output(self, min_input, max_input):
        self.continuous = True
        self.min_input = min_input
        self.max_input = max_input
    
    def disable_continuous_output(self):
        self.continuous = False
    
    def set_integrator_range(self, min_integral, max_integral):
        self.min_integral = min_integral
        self.max_integral = max_integral

    def set_tolerance(self, error_tolerance, error_derivative_tolerance):
        self.error_tolerance = error_tolerance
        self.error_derivative_tolerance = error_derivative_tolerance
    
    def calculate(self, measurement):
        self.measurement = measurement
        self.prev_error = self.error
        self.have_measurement = True

        self.error = self.setpoint - self.measurement

        self.error_derivative = (self.error - self.prev_error) / self.period

        if (abs(self.error) > self.i_zone):
            self.total_error = 0
        elif (self.ki != 0):
            self.total_error = np.clip(self.total_error + self.error * self.period,
                                        self.min_integral / self.ki,
                                        self.max_integral / self.ki)
            
        return self.kp * self.error + self.ki * self.total_error + self.kd * self.error_derivative

    def reset_all(self):
        self.error = 0
        self.prev_error = 0
        self.total_error = 0
        self.error_derivative = 0
        self.have_measurement = False
