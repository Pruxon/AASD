from enum import Enum
from random import random
from math import sin, cos, radians, degrees, atan2


class VehicleType(Enum):
    Normal = 1
    Emergency = 2
    Crashed = 3


DEFAULT_SPEED = 3.0
DEFAULT_CHANCE_TO_CHANGE_DIRECTION = 0.01


class Vehicle:
    def __init__(
        self,
        vehicle_id: str,  # has to be same as the agent id
        x: float = 5.0,
        y: float = 5.0,
        direction: float = 90.0,  # Domyślnie w prawo
        vehicle_type: VehicleType = VehicleType.Normal,
        speed: float = DEFAULT_SPEED,
        random_direction_change_chance: float = DEFAULT_CHANCE_TO_CHANGE_DIRECTION
    ):
        self.id = vehicle_id
        self.x = x
        self.y = y
        self.direction = direction
        self.type = vehicle_type
        self.speed = speed
        self.random_direction_change_chance = random_direction_change_chance
        self.stop_counter: int = 0  # ile razy nie zmienił położenia
        self.previous_speed: float = 0.0

    def move(self, max_x: int, max_y: int):
        if random() < self.random_direction_change_chance:
            self.random_direction_change()

        x = self.x + sin(radians(self.direction)) * self.speed
        y = self.y + cos(radians(self.direction)) * self.speed
        if x < 5.0:
            x = 5.0
            self.random_direction_change()
        elif x > max_x:
            x = float(max_x)
            self.random_direction_change()
        if y < 5.0:
            y = 5.0
            self.random_direction_change()
        elif y > max_y:
            y = float(max_y)
            self.random_direction_change()

        if self.x == x and self.y == y and self.speed != 0.0:
            self.stop_counter += 1
            if self.stop_counter > 2:
                self.stop_counter = 0
                self.reverse_direction()

        self.x = x
        self.y = y

    def random_direction_change(self):
        self.direction += (random() - 0.5) * 180

    def reverse_direction(self):
        self.direction = float((int(self.direction) + 180) % 360)

    def change_direction(self, direction: float):
        self.direction = direction

    def change_direction_to_face_coordinates(self, x: float, y: float):
        self.direction = degrees(atan2(x - self.x, y - self.y))

    def get_coordinates(self) -> tuple[float, float]:
        return self.x, self.y

    def get_direction(self) -> float:
        return self.direction

    def set_speed(self, speed: float):
        self.speed = speed

    def stop(self):
        self.previous_speed = self.speed
        self.speed = 0.0

    def continue_moving(self):
        self.speed = self.previous_speed
        if self.speed == 0.0:
            self.speed = DEFAULT_SPEED

    def disable_random_direction_changes(self):
        self.random_direction_change_chance = 0.0

    def enable_random_direction_changes(self):
        self.random_direction_change_chance = DEFAULT_CHANCE_TO_CHANGE_DIRECTION
