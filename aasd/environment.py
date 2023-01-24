from math import dist, inf
from typing import Optional
from random import random, choice

from aasd.vehicle import Vehicle, VehicleType


class Environment:
    def __init__(self, width: int = 1280, height: int = 720, object_size: int = 10, chance_to_crash: float = 0.001):
        self.width = width
        self.height = height
        self.obj_size: int = object_size
        self.vehicles: list[Vehicle] = []
        self.chance_to_crash: float = chance_to_crash

    def register_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)

    def unregister_vehicle(self, vehicle: Vehicle):
        self.vehicles.remove(vehicle)

    def get_emergency_vehicles(self) -> list[Vehicle]:
        return [
            vehicle
            for vehicle in self.vehicles
            if vehicle.type is VehicleType.Emergency
        ]

    def get_nearby_vehicles(self, caller: Vehicle, radius: float):
        return [
            vehicle
            for vehicle in self.vehicles
            if is_nearby(vehicle, caller, radius) and vehicle is not caller
        ]

    def get_random_coordinates(self) -> tuple[float, float]:
        x = random() * self.width + 5
        y = random() * self.height + 5
        if x > self.width:
            x = float(self.width)
        if y > self.height:
            y = float(self.height)
        return x, y

    def move_vehicles(self):
        for vehicle in self.vehicles:
            vehicle.move(self.width - self.obj_size, self.height - self.obj_size)

    def make_random_accident(self) -> str:
        vehicle = choice(self.vehicles)
        vehicle.type = VehicleType.Crashed
        return vehicle.id

    def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        for vehicle in self.vehicles:
            if vehicle.id == vehicle_id:
                return vehicle
        else:
            return None

    def get_closest_emergency_vehicle(self, x: float, y: float):
        emergency_vehicles = [v for v in self.vehicles if v.type is VehicleType.Emergency]
        closest_ev = None
        lowest_distance = inf
        for ev in emergency_vehicles:
            distance = dist(ev.get_coordinates(), (x, y))
            if distance < lowest_distance:
                lowest_distance = distance
                closest_ev = ev
        return closest_ev

    def are_vehicles_nearby(self, id1: str, id2: str, radius: float) -> bool:
        return is_nearby(self.get_vehicle(id1), self.get_vehicle(id2), radius)


def is_nearby(vehicle1: Optional[Vehicle], vehicle2: Optional[Vehicle], radius: float) -> bool:
    if vehicle1 is None or vehicle2 is None:
        return False
    return dist(vehicle1.get_coordinates(), vehicle2.get_coordinates()) <= radius
