from tkinter import *
from random import random, choice

from aasd.environment import Environment
from aasd.vehicle import Vehicle, VehicleType


class MovementSimulationWindow:
    def __init__(self, environment: Environment):
        self.window = Tk()
        self.canvas = Canvas(
            self.window,
            bg="black",
            height=environment.height,
            width=environment.width,
        )
        self.environment = environment
        self.obj_size = environment.obj_size
        self.left_up_offset = 5
        self.objects: dict[str, int] = {}
        for v in environment.vehicles:
            self.add_object(v.id, v.type, int(v.x), int(v.y))
        self.canvas.pack(padx=1, pady=1)

    def add_object(self, vehicle_id: str, vehicle_type: VehicleType, x: int, y: int):
        color = get_color(vehicle_type)
        assert vehicle_id not in self.objects.keys()
        self.objects[vehicle_id] = self.canvas.create_oval(
            x, y, x + self.obj_size, y + self.obj_size, fill=color
        )

    def get_object_coordinates(self, obj) -> tuple[int, int]:
        x, y, _, _ = self.canvas.coords(obj)
        return x, y

    def start(self):
        self.environment.move_vehicles()
        for v in self.environment.vehicles:
            obj = self.objects[v.id]
            self.canvas.itemconfig(obj, fill=get_color(v.type))
            self.canvas.moveto(obj, int(v.x), int(v.y))

        self.canvas.after(20, self.start)


def get_color(vehicle_type: VehicleType) -> str:
    if vehicle_type is VehicleType.Emergency:
        return "blue"
    elif vehicle_type is VehicleType.Normal:
        return "yellow"
    elif vehicle_type is VehicleType.Crashed:
        return "red"


if __name__ == "__main__":
    env = Environment()
    vehicles = [
        Vehicle("1", 200, 200, vehicle_type=VehicleType.Emergency),
        Vehicle("2", 600, 600),
        Vehicle("3", 400, 700, vehicle_type=VehicleType.Crashed),
    ]
    for vehicle in vehicles:
        env.register_vehicle(vehicle)

    simulation = MovementSimulationWindow(env)

    simulation.start()

    mainloop()
