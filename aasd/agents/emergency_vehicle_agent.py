import asyncio
import spade as spade
import json as json
from spade.template import Template
from aasd.environment import Vehicle, Environment


class EmergencyVehicleAgent(spade.agent.Agent):
    def __init__(self, vehicle: Vehicle, env: Environment, *args, **kwargs):
        self.vehicle = vehicle
        self.env = env
        self.is_assigned = False
        self.accident_x = 0.0
        self.accident_y = 0.0
        super().__init__(*args, **kwargs)

    class UnassignedEvBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def on_start(self) -> None:
            print(f"{str(self.agent.jid)} using unassigned behaviour...")

        async def run(self):
            msg = await self.receive()
            if msg and not self.agent.is_assigned:
                accident_info = json.loads(msg.body)
                self.agent.accident_x = accident_info["x"]
                self.agent.accident_y = accident_info["y"]
                self.agent.is_assigned = True

                print(
                    f"{str(self.agent.jid)}: dispatch message received to accident at x={self.agent.accident_x}, y={self.agent.accident_y}"
                )

    class AlertOtherVehiclesBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def on_start(self) -> None:
            print(f"{str(self.agent.jid)} is starting to alert other vehicles...")

        async def run(self):
            await asyncio.sleep(2)
            nearby_vehicles = self.env.get_nearby_vehicles(self.vehicle, 10)
            for vehicle in nearby_vehicles:
                msg = spade.message.Message(to=vehicle.id)
                msg.set_metadata("msgType", "emergencyVehicleInfo")
                x, y = self.agent.vehicle.get_coordinates()
                msg.body = json.dumps(
                    {"x": x, "y": y, "direction": self.agent.vehicle.get_direction()}
                )
                await self.send(msg)

    class CheckIfArrivedBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def on_start(self) -> None:
            acc_x, acc_y = self.agent.accident_x, self.agent.accident_y
            v_x, v_y = self.agent.vehicle.get_coordinates()

            self.agent.vehicle.change_direction()
            print(
                f"{str(self.agent.jid)} is starting to check if it arrived at the destination..."
            )

        async def run(self):
            await asyncio.sleep(2)
            nearby_vehicles = self.env.get_nearby_vehicles(self.vehicle, 10)
            for vehicle in nearby_vehicles:
                msg = spade.message.Message(to=vehicle.id)
                msg.set_metadata("msgType", "emergencyVehicleInfo")
                x, y = self.agent.vehicle.get_coordinates()
                msg.body = json.dumps(
                    {"x": x, "y": y, "direction": self.agent.vehicle.get_direction()}
                )
                await self.send(msg)

    async def propagateEmergencyVehicleInfo(self, message: spade.message.Message):
        nearby_vehicles = self.env.get_nearby_vehicles(self.vehicle, 5)
        for vehicle in nearby_vehicles:
            msg = spade.message.Message(to=vehicle.id)
            msg.set_metadata("msgType", "emergencyVehicleInfo")
            msg.body = message.body
            await self.send(msg)

    async def setup(self):
        pass
        # print(str(self.jid) + " is starting")
        # t1 = Template()
        # t1.set_metadata("msgType", "evLocationData")
        # self.add_behaviour(
        #     self.HandleForEmergencyVehicleIncomingBehaviour(agent=self), template=t1
        # )
        # t2 = Template()
        # t2.set_metadata("msgType", "helpArrivalInfo")
        # self.add_behaviour(self.HandleHelpArrivalInfoBehaviour(agent=self), template=t2)
