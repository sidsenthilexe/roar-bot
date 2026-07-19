"""
Competition instructions:
Please do not change anything else but fill out the to-do sections.
"""

from typing import List, Tuple, Dict, Optional
import roar_py_interface
import numpy as np
import matplotlib.pyplot as plt
from util.SpeedMap import SpeedMap
from util.SteerMap import SteerMap
from util.WaypointCalculator import WaypointCalculator
from util.PIDController import PIDController

def normalize_rad(rad : float):
    return (rad + np.pi) % (2 * np.pi) - np.pi

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
        # TODO: You can do some initial computation here if you want to.
        # For example, you can compute the path to the first waypoint.

        # Receive location, rotation and velocity data 
        vehicle_location = self.location_sensor.get_last_gym_observation()
        vehicle_rotation = self.rpy_sensor.get_last_gym_observation()
        vehicle_velocity = self.velocity_sensor.get_last_gym_observation()

        self.current_waypoint_idx = 10
        self.current_waypoint_idx = filter_waypoints(
            vehicle_location,
            self.current_waypoint_idx,
            self.maneuverable_waypoints
        )

        self.speed_controller = PIDController(0.1, 0.0, 0.0, 0.05)


    async def step(
        self
    ) -> None:
        """
        This function is called every world step.
        Note: You should not call receive_observation() on any sensor here, instead use get_last_observation() to get the last received observation.
        You can do whatever you want here, including apply_action() to the vehicle.
        """
        # TODO: Implement your solution here.

        # Receive location, rotation and velocity data 
        vehicle_location = self.location_sensor.get_last_gym_observation()
        vehicle_rotation = self.rpy_sensor.get_last_gym_observation()
        vehicle_velocity = self.velocity_sensor.get_last_gym_observation()
        vehicle_velocity_norm = np.linalg.norm(vehicle_velocity)
        
        # Find the waypoint closest to the vehicle
        self.current_waypoint_idx = filter_waypoints(
            vehicle_location,
            self.current_waypoint_idx,
            self.maneuverable_waypoints
        )

        #
        look_ahead = SteerMap.look_ahead_dist(vehicle_velocity_norm)

         # We use the 3rd waypoint ahead of the current waypoint as the target waypoint
        current_waypoint = self.maneuverable_waypoints[self.current_waypoint_idx]
        target_waypoint = self.maneuverable_waypoints[(self.current_waypoint_idx + look_ahead) % len(self.maneuverable_waypoints)]

        spd_look_ahead = np.cliip(int(vehicle_velocity_norm), 20, 50)


        
        speed_wp_1 = self.maneuverable_waypoints[(self.current_waypoint_idx + spd_look_ahead) % len(self.maneuverable_waypoints)]

        speed_wp_2 = self.maneuverable_waypoints[(self.current_waypoint_idx + spd_look_ahead+20) % len(self.maneuverable_waypoints)]

        vector_wp_1 = WaypointCalculator.vector_to_waypoint(speed_wp_1, current_waypoint)
        
        vector_wp_2 = WaypointCalculator.vector_to_waypoint(speed_wp_2, speed_wp_1)

        hdg_wp_1 = WaypointCalculator.hdg(vector_wp_1)

        hdg_wp_2 = WaypointCalculator.hdg(vector_wp_2)

        first_element_dist = WaypointCalculator.dist(speed_wp_1, current_waypoint)

        second_element_dist = WaypointCalculator.dist(speed_wp_1, speed_wp_2)

        heading_diff = normalize_rad(hdg_wp_2 - hdg_wp_1)

        curvature = abs(heading_diff) / (first_element_dist + second_element_dist)

        # Calculate delta vector towards the target waypoint
        vector_to_waypoint = (target_waypoint.location - vehicle_location)[:2]
        heading_to_waypoint = np.arctan2(vector_to_waypoint[1],vector_to_waypoint[0])

        # Calculate delta angle towards the target waypoint
        delta_heading = normalize_rad(heading_to_waypoint - vehicle_rotation[2])

        # Proportional controller to steer the vehicle towards the target waypoint
        steer_control = (
            -12.0 / np.sqrt(vehicle_velocity_norm) * delta_heading / np.pi
        ) if vehicle_velocity_norm > 1e-2 else -np.sign(delta_heading)
        steer_control = np.clip(steer_control, -1.0, 1.0)

        target_speed = SpeedMap.get_target(curvature)

        self.speed_controller.set_setpoint(target_speed)
        throttle_control = self.speed_controller.calculate(vehicle_velocity_norm)

        control = {
            "throttle": np.clip(throttle_control, 0.0, 1.0),
            "steer": steer_control,
            "brake": np.clip(-throttle_control, 0.0, 1.0),
            "hand_brake": 0.0,
            "reverse": 0,
            "target_gear": 0
        }
        print(f"Current waypoint idx: {self.current_waypoint_idx}, Curvature: {curvature}, Target Speed: {target_speed}, Current Speed: {vehicle_velocity_norm}, Throttle%: {throttle_control}")
        await self.vehicle.apply_action(control)
        return control
