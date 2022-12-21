import asyncio
import spade as spade
import json as json
from spade.template import Template
from aasd.environment import Environment
from aasd.vehicle import Vehicle, VehicleType
from math import dist


class TrafficParticipantAgent(spade.agent.Agent):
    def __init__(
        self,
        vehicle: Vehicle,
        env: Environment,
        chance_to_crash: float = 0.0,
        *args,
        **kwargs
    ):
        self.vehicle = vehicle
        self.env = env
        self.is_crashed = False
        self.is_help_dispatched = False
        self.chance_to_crash = chance_to_crash
        super().__init__(*args, **kwargs)

    def displayAlertBehaviour(self):
        print("Jedzie Karetka!")

    async def propagateEmergencyVehicleInfo(self, message: spade.message.Message):
        nearby_vehicles = self.env.get_nearby_vehicles(self.vehicle, 5)
        for vehicle in nearby_vehicles:
            msg = spade.message.Message(to=vehicle.id)
            msg.set_metadata("msgType", "emergencyVehicleInfo")
            msg.body = message.body
            await self.send(msg)

    def createAccidentMessagebody(self, x: float, y: float) -> str:
        dictionary = {"x": x, "y": y, "message": "Accident happened, help needed"}
        return json.dumps(dictionary)

    async def informManagerAfterAccident(self, x: float, y: float):
        msg = spade.message.Message(to="manager@localhost")
        msg.set_metadata("performative", "inform")
        msg.set_metadata("msgType", "accidentInfo")
        msg.body = self.createAccidentMessagebody(x, y)
        await self.send(msg)

    def crash(self):
        self.is_crashed = True
        self.is_help_dispatched = False
        self.add_behaviour(self.InformManagerBehaviour(agent=self))

    class InformManagerBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def run(self):
            if self.agent.is_help_dispatched:
                self.kill()
            else:
                self.agent.informManagerAfterAccident(
                    self.agent.vehicle.x, self.agent.vehicle.y
                    )

                await asyncio.sleep(1)

    class WaitForEmergencyVehicleBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, ev_id: str, **kwargs):
            self.agent = agent
            self.ev_id = ev_id
            super().__init__(**kwargs)

        async def run(self):
            if self.agent.env.is_nearby_by_id(self.agent.vehicle.id, self.ev_id):
                self.agent.vehicle.continue_moving()
                self.agent.vehicle.type = VehicleType.Normal
                self.kill()
            else:
                await asyncio.sleep(1)

    class HandleForEmergencyVehicleIncomingBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def run(self):
            msg = await self.receive()
            if msg:
                body = msg.body
                x=body["x"]
                y=body["y"]
                ev_coordinates = tuple[x, y]
                direction=body["direction"]
                if self.check_if_ev_is_nearby(ev_coordinates, 40):
                    self.agent.vehicle.change_direction(direction=self.calculate_direction(ev_coordinates= ev_coordinates, ev_direction=direction))
                    self.agent.propagateEmergencyVehicleInfo(self=self.agent, message=msg)

        def check_if_ev_is_nearby(self, ev_coordinates: tuple[float, float], radius: float) -> bool:
            return dist(self.agent.vehicle.get_coordinates(), ev_coordinates) <= radius

        def calculate_direction(self, ev_coordinates: tuple[float, float], ev_direction: float) -> float:


    class HandleHelpArrivalInfoBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def run(self):
            msg = await self.receive()
            if msg:
                print("Help is arriving in: " + msg.body)
                ev_info = json.loads(msg.body)
                evId = ev_info["ev_id"]
                self.agent.is_help_dispatched = True
                self.agent.add_behaviour(self.agent.WaitForEmergencyVehicleBehaviour(agent=self.agent, ev_id=evId))

    async def setup(self):
        print(str(self.jid) + " is starting")
        t1 = Template()
        t1.set_metadata("msgType", "evLocationData")
        self.add_behaviour(
            self.HandleForEmergencyVehicleIncomingBehaviour(agent=self), template=t1
        )
        t2 = Template()
        t2.set_metadata("msgType", "helpArrivalInfo")
        self.add_behaviour(self.HandleHelpArrivalInfoBehaviour(agent=self), template=t2)
