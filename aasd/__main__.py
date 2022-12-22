import time
import asyncio
from tkinter import *
import threading

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template

from aasd.agents.manager_agent import ManagerAgent
from aasd.agents.traffic_participant_agent import TrafficParticipantAgent
from aasd.agents.emergency_vehicle_agent import EmergencyVehicleAgent
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
    ev1_user = UserToRegister("ev1")
    ev2_user = UserToRegister("ev2")
    tp1_user = UserToRegister("tp1")
    tp2_user = UserToRegister("tp2")
    tp3_user = UserToRegister("tp3")
    tp4_user = UserToRegister("tp4")

    register_users_to_ejabberd(
        [manager_user, ev1_user, ev2_user, tp1_user, tp2_user, tp3_user, tp4_user]
    )

    manager = ManagerAgent(manager_user.jid_str(), manager_user.password)
    manager.start().wait()

    ev1_v = Vehicle(ev1_user.jid_str(), 300, 700, vehicle_type=VehicleType.Emergency)
    env.register_vehicle(ev1_v)
    ev1 = EmergencyVehicleAgent(
        vehicle=ev1_v, env=env, jid=ev1_user.jid_str(), password=ev1_user.password
    )
    ev1.start().wait()

    ev2_v = Vehicle(ev2_user.jid_str(), 600, 800, vehicle_type=VehicleType.Emergency)
    env.register_vehicle(ev2_v)
    ev2 = EmergencyVehicleAgent(
        vehicle=ev2_v, env=env, jid=ev2_user.jid_str(), password=ev2_user.password
    )
    ev2.start().wait()

    tp1_v = Vehicle(tp1_user.jid_str(), 500, 500, vehicle_type=VehicleType.Normal)
    env.register_vehicle(tp1_v)
    tp1 = TrafficParticipantAgent(
        vehicle=tp1_v,
        env=env,
        jid=tp1_user.jid_str(),
        password=tp1_user.password,
        chance_to_crash=0.01,
    )
    tp1.start().wait()

    tp2_v = Vehicle(tp2_user.jid_str(), 500, 500, vehicle_type=VehicleType.Normal)
    env.register_vehicle(tp2_v)
    tp2 = TrafficParticipantAgent(
        vehicle=tp2_v,
        env=env,
        jid=tp2_user.jid_str(),
        password=tp2_user.password,
        chance_to_crash=0.01,
    )
    tp2.start().wait()

    tp3_v = Vehicle(tp3_user.jid_str(), 500, 500, vehicle_type=VehicleType.Normal)
    env.register_vehicle(tp3_v)
    tp3 = TrafficParticipantAgent(
        vehicle=tp3_v,
        env=env,
        jid=tp3_user.jid_str(),
        password=tp3_user.password,
        chance_to_crash=0.01,
    )
    tp3.start().wait()

    tp4_v = Vehicle(tp4_user.jid_str(), 500, 500, vehicle_type=VehicleType.Normal)
    env.register_vehicle(tp4_v)
    tp4 = TrafficParticipantAgent(
        vehicle=tp4_v,
        env=env,
        jid=tp4_user.jid_str(),
        password=tp4_user.password,
        chance_to_crash=0.01,
    )
    tp4.start().wait()

    simulation = MovementSimulationWindow(env)

    simulation.start()

    mainloop()
