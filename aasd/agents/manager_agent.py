import spade as spade
from spade.template import Template

from dataclasses import dataclass
import json


@dataclass
class EvStatus:
    id: str
    x: float
    y: float
    assigned: bool


class ManagerAgent(spade.agent.Agent):
    class HandleAccidentInfoBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, ev: list[EvStatus], **kwargs):
            self.emergency_vehicles = ev
            super().__init__(**kwargs)

        async def on_start(self) -> None:
            print("Manager is listening for accident info...")

        async def run(self):
            msg = await self.receive()
            if msg:
                print(f"Message AccidentInfo received:\n{msg}")
                print(msg.sender)
                print(msg.get_metadata("performative"))

    class HandleEmergencyVehicleInfoBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, ev: list[EvStatus], **kwargs):
            self.emergency_vehicles = ev
            super().__init__(**kwargs)

        async def on_start(self) -> None:
            print("Manager is listening for emergency vehicle info...")

        async def run(self):
            msg = await self.receive()
            if msg:
                ev_info = json.loads(msg.body)
                ev_id = msg.sender
                self.emergency_vehicles[ev_id] = EvStatus(
                    id=ev_id,
                    x=ev_info["x"],
                    y=ev_info["y"],
                    assigned=ev_info["assigned"],
                )

                print(
                    f"EmergencyVehicleInfo message received: {self.emergency_vehicles[ev_id]}"
                )

    async def setup(self) -> None:
        self.agent = self
        print("Manager is starting")
        self.emergency_vehicles: dict[str, EvStatus] = {}

        t1 = Template()
        t1.set_metadata("msgType", "accidentInfo")
        self.add_behaviour(
            self.HandleAccidentInfoBehaviour(ev=self.emergency_vehicles), template=t1
        )
        t2 = Template()
        t2.set_metadata("msgType", "emergencyVehicleInfo")
        self.add_behaviour(
            self.HandleEmergencyVehicleInfoBehaviour(ev=self.emergency_vehicles),
            template=t2,
        )
