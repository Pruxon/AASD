import time
import asyncio
from tkinter import *

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template

from aasd.agents.manager_agent import ManagerAgent
from aasd.agents.traffic_participant_agent import TrafficParticipantAgent
from aasd.gui import MovementSimulationWindow, get_color
from aasd.environment import Environment
from aasd.vehicle import Vehicle, VehicleType
from aasd.ejabberd_register import register_users_to_ejabberd, UserToRegister


class SenderAgent(Agent):
    class InformBehav(OneShotBehaviour):
        async def run(self):

            msg = Message(to="manager@localhost")
            msg.set_metadata("performative", "inform")
            msg.set_metadata("msgType", "emergencyVehicleInfo")
            msg.body = '{"x": 1.0, "y": 0.1, "assigned": false}'

            await self.send(msg)
            print("Message sent!")

            await asyncio.sleep(1)

            print("InformBehav running")
            msg = Message(to="manager@localhost")
            msg.set_metadata("performative", "request")
            msg.set_metadata("msgType", "accidentInfo")
            msg.body = '{"x": 20.0, "y": 0.0}'

            await self.send(msg)
            print("Message 2 sent!")

            # stop agent from behaviour
            await self.agent.stop()

    async def setup(self):
        print("SenderAgent started")
        b = self.InformBehav()
        self.add_behaviour(b)


if __name__ == "__main__":
    env = Environment()

    manager_user = UserToRegister("manager")
    tp1_user = UserToRegister("tp1")

    register_users_to_ejabberd([manager_user, tp1_user])

    manager = ManagerAgent(manager_user.jid_str(), manager_user.password)
    manager.start().wait()

    v1 = Vehicle(tp1_user.jid_str(), 500, 500, vehicle_type=VehicleType.Normal)
    env.register_vehicle(v1)
    tp1 = TrafficParticipantAgent(
        vehicle=v1, env=env, jid=tp1_user.jid_str(), password=tp1_user.password
    )
    tp1.start().wait()

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
