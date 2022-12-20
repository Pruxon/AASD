from enum import Enum
from random import randint, random, choice


class VehicleType(Enum):
    Normal = 1
    Emergency = 2


class Direction(Enum):
    Left = 1
    Up = 2
    Right = 3
    Down = 4


class Environment:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.vehicles = []
        self.location_cache: dict[str, tuple[int, int]] = {}  # mapowanie id pojazdu na wspólrzędne x, y

    def register_vehicle(self, vehicle):
        self.vehicles.append(vehicle)
        self.location_cache[vehicle.id] = vehicle.x, vehicle.y

    def unregister_vehicle(self, vehicle):
        self.vehicles.remove(vehicle)
        self.location_cache.pop(vehicle.id)

    def get_emergency_vehicles(self):
        return [vehicle for vehicle in self.vehicles if vehicle.type is VehicleType.Emergency]

    def get_nearby_vehicles(self, caller, reach: int):
        """
        reach - zasięg, żeby nie bawić się w floaty zasięg określany metryką położenie +/- reach w osi x i y
        """
        return [vehicle for vehicle in self.vehicles if is_nearby(vehicle, caller, reach)]

    def get_random_coordinates(self) -> tuple[int, int]:
        return randint(0, self.width), randint(0, self.height)

    def move_vehicle(self, vehicle):
        new_x = vehicle.new_x()
        new_y = vehicle.new_y()
        if new_x < 0:
            new_x = 0
        elif new_x >= self.width:
            new_x = self.width - 1

        if new_y < 0:
            new_y = 0
        elif new_y >= self.height:
            new_y = self.height - 1

        vehicle.move(new_x, new_y)
        self.location_cache[vehicle.id] = new_x, new_y

        if random() < 0.2:
            vehicle.random_change_direction()

    def make_random_accident(self):
        vehicle = choice(self.vehicles)
        vehicle.crash()


class Vehicle:
    def __init__(self, x: int, y: int, direction: Direction, vehicle_type: VehicleType):
        self.x = x
        self.y = y
        self.direction = direction
        self.agent = None  # konstruowanie agenta z rejestracją na XMPP
        self.is_crashed = True
        self.type = vehicle_type

    def new_x(self):
        if self.direction == Direction.Left:
            return self.x - 1
        elif self.direction == Direction.Right:
            return self.x + 1
        else:
            return self.x

    def new_y(self):
        if self.direction == Direction.Down:
            return self.x - 1
        elif self.direction == Direction.Up:
            return self.x + 1
        else:
            return self.x

    def move(self, x: int, y: int):
        self.x, self.y = x, y

    def random_change_direction(self):
        self.direction = Direction(randint(1, 5))

    def change_direction(self, direction: Direction):
        self.direction = direction

    def crash(self):
        self.is_crashed = True


def is_nearby(vehicle1, vehicle2, reach: int) -> bool:
    x_nearby = abs(vehicle1.x - vehicle2.x) <= reach
    y_nearby = abs(vehicle1.y - vehicle2.y) <= reach
    return x_nearby and y_nearby
