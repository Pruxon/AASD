import asyncio
import spade as spade
import json as json
from random import random
from spade.template import Template
from aasd.environment import Environment
from aasd.vehicle import Vehicle, VehicleType
from math import dist, sin, cos, radians
from numpy import sign


class TrafficParticipantAgent(spade.agent.Agent):
    def __init__(
        self,
        vehicle: Vehicle,
        env: Environment,
        *args,
        **kwargs,
    ):
        self.vehicle: Vehicle = vehicle
        self.env = env
        self.is_crashed = False
        self.is_help_dispatched = False
        super().__init__(*args, **kwargs)

    def prune_behaviours(self):
        for b in self.behaviours:
            self.remove_behaviour(b)

    def init_uncrashed_behaviour(self):
        print(f"{str(self.jid)}: switching to uncrashed behaviour")
        self.is_crashed = False
        self.prune_behaviours()
        t1 = Template()
        t1.set_metadata("msgType", "evLocationData")
        self.add_behaviour(
            self.HandleEmergencyVehicleInfoIncomingBehaviour(agent=self), template=t1
        )
        self.add_behaviour(self.RandomCrashBehaviour(agent=self))

    def init_communicate_crash_behaviour(self):
        print(f"{str(self.jid)}: switching to communicate_crash behaviour")
        self.prune_behaviours()
        t1 = Template()
        t1.set_metadata("msgType", "helpArrivalInfo")
        self.add_behaviour(self.HandleHelpArrivalInfoBehaviour(agent=self), template=t1)
        self.add_behaviour(self.InformManagerBehaviour(agent=self))

    def init_crash_wait_for_help_behaviour(self):
        print(f"{str(self.jid)}: switching to crash_wait_for_help behaviour")
        self.prune_behaviours()
        self.add_behaviour(self.WaitForEmergencyVehicleBehaviour(agent=self))

    async def propagateEmergencyVehicleInfo(self, message: spade.message.Message):
        nearby_vehicles = self.env.get_nearby_vehicles(self.vehicle, 50)
        for vehicle in nearby_vehicles:
            msg = spade.message.Message(to=vehicle.id)
            msg.set_metadata("msgType", "evLocationData")
            msg.body = message.body
            await self.send(msg)

    def createAccidentMessagebody(x: float, y: float) -> str:
        dictionary = {"x": x, "y": y, "message": "Accident happened, help needed"}
        return json.dumps(dictionary)

    def crash(self):
        self.is_crashed = True
        self.is_help_dispatched = False
        self.vehicle.type = VehicleType.Crashed
        self.vehicle.stop()
        self.init_communicate_crash_behaviour()

    class InformManagerBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def run(self):
            if self.agent.is_help_dispatched:
                self.kill()
            else:
                msg = spade.message.Message(to="manager@localhost")
                msg.set_metadata("performative", "inform")
                msg.set_metadata("msgType", "accidentInfo")
                x, y = self.agent.vehicle.get_coordinates()
                msg.body = json.dumps(
                    {"x": x, "y": y, "message": "Accident happened, help needed"}
                )
                await self.send(msg)

                await asyncio.sleep(1)

'''
Behaviour launching after getting message from Manager that help is arriving
'''
    class WaitForEmergencyVehicleBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, ev_id: str, **kwargs):
            self.agent = agent
            self.ev_id = ev_id
            super().__init__(**kwargs)

        async def run(self):
            if self.agent.env.are_vehicles_nearby(self.agent.vehicle.id, self.ev_id, 10.0):
                await asyncio.sleep(0.5)
                self.agent.vehicle.continue_moving()
                self.agent.vehicle.type = VehicleType.Normal
                self.agent.init_uncrashed_behaviour()
            else:
                await asyncio.sleep(0.1)

'''
Behaviour for reveiving and propagating evLocationData message
'''
    class HandleEmergencyVehicleInfoIncomingBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def run(self):
            msg = await self.receive()
            if msg:
                print("BBBBBBBBBBBBBBBBBBB")
                body = json.loads(msg.body)
                x = body["x"]
                y = body["y"]
                ev_coordinates = tuple[x, y]
                print(ev_coordinates)
                direction = body["direction"]
                if self.check_if_ev_is_nearby(ev_coordinates, 100.0):
                    print("AAAAAAAAAAAAAAAAAAAAAAAAA")
                    self.agent.vehicle.change_direction(
                        direction=self.calculate_direction(
                            x1=x, y1=y, ev_direction=direction
                        )
                    )
                    print("ev dir: " + direction + " ev coords" + ev_coordinates + " own dir" + self.agent.vehicle.get_direction() + " own coords:" + self.agent.vehicle.get_coordinates())
                    self.agent.propagateEmergencyVehicleInfo(
                        self=self.agent, message=msg
                    )
#TODO poprawic tu bo wywala na dist, jedno printuje [x,y] drugie (x,y) xD
        def check_if_ev_is_nearby(
            self, ev_coordinates: tuple[float, float], radius: float
        ) -> bool:
            print(ev_coordinates)
            a = tuple[self.agent.vehicle.x, self.agent.vehicle.y]
            print(self.agent.vehicle.get_coordinates())
            print("CCCCCCCCCCCCCCCCCCCCCCCCCCC")
            return dist(a, ev_coordinates) <= radius

        def calculate_direction(
            self, x1: float, y1: float, ev_direction: float
        ) -> float:
            x = self.agent.vehicle.x
            y = self.agent.vehicle.y
            x2 = self.ev_x + sin(radians(self.ev_direction)) * 3.0
            y2 = self.ev_y + cos(radians(self.ev_direction)) * 3.0
            position = sign((x - x1) * (y2 - y1) - (y - y1) * (x2 - x1))

            if position >= 0:
                return ev_direction + 90.0
            else:
                return ev_direction - 90.0

    class RandomCrashBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def run(self):
            await asyncio.sleep(0.1)
            if not self.agent.is_crashed and random() < self.agent.environment.chance_to_crash:
                self.agent.crash()
'''
Behaviour for handling message with Arrival info, launches waiting for emergency
'''
    class HandleHelpArrivalInfoBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def run(self):
            msg = await self.receive()
            if msg:
                print("Help is arriving in: " + msg.body)
                ev_info = json.loads(msg.body)
                evId = ev_info["vehicle_id"]
                self.agent.is_help_dispatched = True
                self.agent.add_behaviour(
                    self.agent.WaitForEmergencyVehicleBehaviour(
                        agent=self.agent, ev_id=evId
                    )
                )

    async def setup(self):
        print(str(self.jid) + " is starting")
        self.init_uncrashed_behaviour()
