import asyncio
import spade as spade
import json as json
from math import dist
from spade.template import Template
from aasd.environment import Vehicle, Environment


class EmergencyVehicleAgent(spade.agent.Agent):
    def __init__(self, vehicle: Vehicle, env: Environment, *args, **kwargs):
        self.vehicle: Vehicle = vehicle
        self.env = env
        self.is_assigned = False
        self.accident_x = 0.0
        self.accident_y = 0.0
        super().__init__(*args, **kwargs)

    def prune_behaviours(self):
        for b in self.behaviours:
            if isinstance(b, self.InformManagerAboutLocationBehaviour):
                continue
            self.remove_behaviour(b)

    def init_undispatched_behaviour(self):
        print(f"{str(self.jid)}: switching to undispatched ev behaviour")
        self.vehicle.random_direction_change()
        self.vehicle.enable_random_direction_changes()
        self.prune_behaviours()
        t1 = Template()
        t1.set_metadata("msgType", "processedAccidentInfo")
        self.add_behaviour(
            self.HandleAccidentDispatchBehaviour(agent=self), template=t1
        )

    def init_dispatched_behaviour(self):
        print(f"{str(self.jid)}: switching to dispatched ev behaviour")
        self.prune_behaviours()
        self.add_behaviour(self.AlertOtherVehiclesBehaviour(agent=self))
        self.add_behaviour(self.CheckIfArrivedBehaviour(agent=self))

    class HandleAccidentDispatchBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def on_start(self) -> None:
            print(f"{str(self.agent.jid)} using HandleAccidentDispatchBehaviour...")

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
                self.agent.init_dispatched_behaviour()

    class InformManagerAboutLocationBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def run(self):
            msg = spade.message.Message(to="manager@localhost")
            msg.set_metadata("performative", "inform")
            msg.set_metadata("msgType", "emergencyVehicleInfo")
            x, y = self.agent.vehicle.get_coordinates()
            msg.body = json.dumps({"x": x, "y": y, "assigned": self.agent.is_assigned})
            await self.send(msg)

            await asyncio.sleep(1)

    class AlertOtherVehiclesBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def on_start(self) -> None:
            print(f"{str(self.agent.jid)} is starting to alert other vehicles...")

        async def run(self):
            await asyncio.sleep(2)
            nearby_vehicles = self.agent.env.get_nearby_vehicles(self.agent.vehicle, 10)
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
            self.agent.vehicle.disable_random_direction_changes()
            self.agent.vehicle.change_direction_to_face_coordinates(
                self.agent.accident_x, self.agent.accident_y
            )
            print(
                f"{str(self.agent.jid)} is starting to check if it arrived at the destination..."
            )

        async def run(self):
            x, y = self.agent.vehicle.get_coordinates()
            if dist((x, y), (self.agent.accident_x, self.agent.accident_y)) < 10.0:
                self.agent.is_assigned = False
                self.agent.init_undispatched_behaviour()
            await asyncio.sleep(0.1)

    async def setup(self):
        print(f"{str(self.jid)} starting...")
        self.add_behaviour(self.InformManagerAboutLocationBehaviour(agent=self))
        self.init_undispatched_behaviour()
