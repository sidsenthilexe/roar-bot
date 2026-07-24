"""
Competition instructions:
Please do not change anything else but fill out the to-do sections.
"""

from typing import List, Tuple, Dict, Optional
import roar_py_interface
import numpy as np
from util.SpeedMap import SpeedMap
from util.MathUtil import MathUtil
from util.PIDController import PIDController
from util.SteerController import SteerController

def filter_waypoints(location : np.ndarray, current_idx: int, waypoints : List[roar_py_interface.RoarPyWaypoint]) -> int:
    def dist_to_waypoint(waypoint : roar_py_interface.RoarPyWaypoint):
        return np.linalg.norm(
            location[:2] - waypoint.location[:2]
        )
    for i in range(current_idx, len(waypoints) + current_idx):
        if dist_to_waypoint(waypoints[i%len(waypoints)]) < 3:
            return i % len(waypoints)
    return current_idx

class RoarCompetitionSolution:
    def __init__(
        self,
        maneuverable_waypoints: List[roar_py_interface.RoarPyWaypoint],
        vehicle : roar_py_interface.RoarPyActor,
        camera_sensor : roar_py_interface.RoarPyCameraSensor = None,
        location_sensor : roar_py_interface.RoarPyLocationInWorldSensor = None,
        velocity_sensor : roar_py_interface.RoarPyVelocimeterSensor = None,
        rpy_sensor : roar_py_interface.RoarPyRollPitchYawSensor = None,
        occupancy_map_sensor : roar_py_interface.RoarPyOccupancyMapSensor = None,
        collision_sensor : roar_py_interface.RoarPyCollisionSensor = None,
    ) -> None:
        self.maneuverable_waypoints = maneuverable_waypoints
        self.vehicle = vehicle
        self.camera_sensor = camera_sensor
        self.location_sensor = location_sensor
        self.velocity_sensor = velocity_sensor
        self.rpy_sensor = rpy_sensor
        self.occupancy_map_sensor = occupancy_map_sensor
        self.collision_sensor = collision_sensor
    
    async def initialize(self) -> None:
        self.maneuverable_waypoints = roar_py_interface.RoarPyWaypoint.load_waypoint_list(np.load("waypoints/output_waypointsPrimary1.npz"))

        vehicle_location = self.location_sensor.get_last_gym_observation()

        self.current_waypoint_idx = 10
        self.current_waypoint_idx = filter_waypoints(
            vehicle_location,
            self.current_waypoint_idx,
            self.maneuverable_waypoints
        )

        self.speed_controller = PIDController(0.9, 0.1, 0.1, 0.05)
        self.steer_controller = PIDController(1.0, 0.0, 0.0, 0.05)

    async def step(
        self
    ) -> None:
        vehicle_location = self.location_sensor.get_last_gym_observation()
        vehicle_rotation = self.rpy_sensor.get_last_gym_observation()
        vehicle_velocity = self.velocity_sensor.get_last_gym_observation()
        vehicle_velocity_norm = np.linalg.norm(vehicle_velocity)
        
        self.current_waypoint_idx = filter_waypoints(
            vehicle_location,
            self.current_waypoint_idx,
            self.maneuverable_waypoints
        ) 


        target_speed = SpeedMap.get_target_speed(vehicle_velocity_norm, self)

        self.speed_controller.set_setpoint(target_speed)
        throttle_control = self.speed_controller.calculate(vehicle_velocity_norm)
        throttle_normalized = np.clip(throttle_control, 0.0, 1.0)
        brake_normalized = np.clip(-throttle_control, 0.0, 1.0)

        target_steer = SteerController.get_target_heading(vehicle_velocity_norm, self, vehicle_location, vehicle_rotation)


        self.steer_controller.set_setpoint(target_steer)
        steer_control = self.steer_controller.calculate(MathUtil.normalize_rad(vehicle_rotation[2]))
        steer_normalized = np.clip(steer_control, -1.0, 1.0)

        #throttle_normalized, brake_normalized, steer_control = MathUtil.clamp_inputs(throttle_normalized, brake_normalized, steer_control)

        control = {
            "throttle": throttle_normalized,
            "steer": steer_normalized,
            "brake": brake_normalized,
            "hand_brake": 0,
            "reverse": 0,
            "target_gear": 0
        }
        print(f"Throttle: {throttle_normalized}, Target Speed: {target_speed}, Current Speed: {vehicle_velocity_norm}, Target Angle: {target_steer}, Current Angle: {vehicle_rotation[2]}, Steer Control: {steer_control}")
        await self.vehicle.apply_action(control)
        return control