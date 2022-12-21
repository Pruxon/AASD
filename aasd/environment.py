from random import random, choice
from math import dist
from .vehicle import Vehicle, VehicleType


class Environment:
    def __init__(self, width: int = 1280, height: int = 720, object_size: int = 10):
        self.width = width
        self.height = height
        self.obj_size: int = object_size
        self.vehicles: list[Vehicle] = []
        self.location_cache: dict[str, tuple[float, float]] = {}  # mapowanie id pojazdu na wspólrzędne x, y

    def register_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)
        self.location_cache[vehicle.id] = vehicle.x, vehicle.y

    def unregister_vehicle(self, vehicle: Vehicle):
        self.vehicles.remove(vehicle)
        self.location_cache.pop(vehicle.id)

    def get_emergency_vehicles(self) -> list[Vehicle]:
        return [vehicle for vehicle in self.vehicles if vehicle.type is VehicleType.Emergency]

    def get_nearby_vehicles(self, caller: Vehicle, radius: float):
        return [vehicle for vehicle in self.vehicles if is_nearby(vehicle, caller, radius)]

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


def is_nearby(vehicle1: Vehicle, vehicle2: Vehicle, radius: float) -> bool:
    return dist(vehicle1.get_coordinates(), vehicle2.get_coordinates()) <= radius

