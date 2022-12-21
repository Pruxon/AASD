from enum import Enum
from random import random
from math import sin, cos, radians


class VehicleType(Enum):
    Normal = 1
    Emergency = 2
    Crashed = 3


class Vehicle:
    def __init__(
            self,
            vehicle_id: str,
            x: float = 5.0,
            y: float = 5.0,
            direction: float = 90.0,  # Domyślnie w prawo
            vehicle_type: VehicleType = VehicleType.Normal
    ):
        #TODO id wehikułu musi być takie samo jak jid agenta, który posiada dany wehikuł
        self.id = vehicle_id
        self.x = x
        self.y = y
        self.direction = direction
        self.type = vehicle_type
        self.stop_counter: int = 0  # ile razy nie zmienił położenia

    def move(self, max_x: int, max_y: int):
        x = self.x + sin(radians(self.direction))
        y = self.y + cos(radians(self.direction))
        if x < 5.0:
            x = 5.0
        elif x > max_x:
            x = float(max_x)
        if y < 5.0:
            y = 5.0
        elif y > max_y:
            y = float(max_y)

        if self.x == x and self.y == y:
            self.stop_counter += 1
            self.reverse_direction()

        self.x = x
        self.y = y

    def random_direction_change(self):
        self.direction += (random() - 0.5) * 10

    def reverse_direction(self):
        if self.stop_counter > 2:
            self.stop_counter = 0
            self.direction = float((int(self.direction) + 180) % 360)

    def change_direction(self, direction: float):
        self.direction = direction

    def get_coordinates(self) -> tuple[float, float]:
        return self.x, self.y

