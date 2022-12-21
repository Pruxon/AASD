from tkinter import *
from random import randint, random, choice

from aasd.environment import VehicleType


class MovementSimulationWindow:
    def __init__(self, width: int = 1280, height: int = 720, vehicle_size: int = 10):
        self.window = Tk()
        self.canvas = Canvas(
            self.window,
            bg='black',
            height=height,
            width=width,
        )
        self.v_size = vehicle_size
        self.width = width
        self.height = height
        self.left_up_offset = 5
        self.vehicles: dict[str, int] = {}

        self.canvas.pack(padx=1, pady=1)

    def add_vehicle(self, vehicle_id: str, vehicle_type: VehicleType, x: int, y: int):
        color = None
        if vehicle_type is VehicleType.Emergency:
            color = 'red'
        elif vehicle_type is VehicleType.Normal:
            color = 'blue'
        elif vehicle_type is VehicleType.Crashed:
            color = 'yellow'

        assert vehicle_id not in self.vehicles.keys()

        self.vehicles[vehicle_id] = self.canvas.create_oval(x, y, x + self.v_size, y + self.v_size, fill=color)

    def start(self):
        for id, vehicle in self.vehicles.items():
            random_x_movement = 0  # randint(-5, 6)
            random_y_movement = 0  # randint(-5, 6)
            if random() < 0.5:
                random_x_movement = choice([1, 2, 3, -1, -2, -3])
            else:
                random_y_movement = choice([1, 2, 3, -1, -2, -3])
            x, y = self.get_vehicle_coordinates(vehicle)
            x_movement, y_movement = self.ensure_movement_correct(x, y, random_x_movement, random_y_movement)
            print(f'vehicleId: {id}, x: {x}, y: {y}, x_move:{x_movement}, y_move: {y_movement}')
            self.canvas.move(vehicle, x_movement, y_movement)

        self.canvas.after(50, self.start)

    def get_vehicle_coordinates(self, vehicle) -> tuple[int, int]:
        x, y, _, _ = self.canvas.coords(vehicle)
        return x, y

    def ensure_movement_correct(self, x: int, y: int, x_move: int, y_move: int):
        corrected_x_movement = 0
        corrected_y_movement = 0
        if x + x_move < self.left_up_offset:
            corrected_x_movement = self.left_up_offset - x
        elif x + x_move > self.width - self.v_size:
            corrected_x_movement = self.width - self.v_size - x
        else:
            corrected_x_movement = x_move

        if y + y_move < self.left_up_offset:
            corrected_y_movement = self.left_up_offset - y
        elif y + y_move > self.height - self.v_size:
            corrected_y_movement = self.height - self.v_size - y
        else:
            corrected_y_movement = y_move

        return corrected_x_movement, corrected_y_movement


if __name__ == "__main__":
    simulation = MovementSimulationWindow()
    simulation.add_vehicle('1', VehicleType.Emergency, 200, 200)
    simulation.add_vehicle('2', VehicleType.Normal, 600, 600)
    simulation.add_vehicle('3', VehicleType.Crashed, 400, 700)

    simulation.start()

    mainloop()
