import spade as spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

from dataclasses import dataclass
from aasd.environment import Environment
import json
from math import sqrt


@dataclass
class EvStatus:
    id: str
    x: float
    y: float
    assigned: bool


class ManagerAgent(Agent):
    def __init__(self, env: Environment, *args, **kwargs):
        self.env = env
        super().__init__(*args, **kwargs)

    class HandleAccidentInfoBehaviour(CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def on_start(self) -> None:
            print("Manager is listening for accident info...")

        def choose_closest_ev(
            self, evs: list[EvStatus], x: float, y: float
        ) -> EvStatus:
            closest_ev: evs = evs[0]
            closest_ev_dist = float("inf")
            for ev in evs[1:]:
                x_diff = ev.x - x
                y_diff = ev.y - y
                dist = sqrt(x_diff * x_diff + y_diff * y_diff)
                if dist < closest_ev_dist:
                    closest_ev = ev
                    closest_ev_dist = dist
            return closest_ev

        async def run(self):
            msg = await self.receive()
            if msg:
                msg_sender = str(msg.sender)
                print(f"ManagerAgent: AccidentInfo msg received from {msg_sender}")
                if msg_sender in self.agent.accident_vehicle_to_ev:
                    return  # duplicate
                dispatchable_evs = [
                    e
                    for _, e in self.agent.emergency_vehicles.items()
                    if not e.assigned
                ]
                if len(dispatchable_evs) == 0:
                    print("ManagerAgent: no EVs to dispatch; aborting")
                    return

                accident_info = json.loads(msg.body)
                x = accident_info["x"]
                y = accident_info["y"]

                # ev_to_dispatch = self.agent.env.get_closest_emergency_vehicle(x, y)

                ev_to_dispatch = self.choose_closest_ev(dispatchable_evs, x, y)
                ev_to_dispatch.assigned = True
                self.agent.emergency_vehicles[ev_to_dispatch.id] = ev_to_dispatch

                msg = Message(to=ev_to_dispatch.id)
                msg.set_metadata("performative", "inform")
                msg.set_metadata("msgType", "processedAccidentInfo")
                msg.body = json.dumps({"x": x, "y": y})

                await self.send(msg)

                msg = Message(to=msg_sender)
                msg.set_metadata("performative", "agree")
                msg.set_metadata("msgType", "helpArrivalInfo")
                msg.body = json.dumps({"ev_id": ev_to_dispatch.id})
                await self.send(msg)

                print(
                    f"ManagerAgent: dispatched EV={ev_to_dispatch.id} to {msg_sender}"
                )

    class HandleEmergencyVehicleInfoBehaviour(CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def on_start(self) -> None:
            print("Manager is listening for emergency vehicle info...")

        async def run(self):
            msg = await self.receive()
            if msg:
                ev_info = json.loads(msg.body)
                ev_id = str(msg.sender)
                status = EvStatus(
                    id=ev_id,
                    x=ev_info["x"],
                    y=ev_info["y"],
                    assigned=ev_info["assigned"],
                )
                self.agent.emergency_vehicles[ev_id] = status
                if not status.assigned:
                    # remove assignment entry for the ev
                    self.agent.accident_vehicle_to_ev = {
                        k: v
                        for k, v in self.agent.accident_vehicle_to_ev.items()
                        if v != ev_id
                    }

                print(
                    f"EmergencyVehicleInfo message received: {self.agent.emergency_vehicles[ev_id]}"
                )

    async def setup(self) -> None:
        print("Manager is starting")
        self.emergency_vehicles: dict[str, EvStatus] = {}
        self.accident_vehicle_to_ev: dict[str, str] = {}

        t1 = Template()
        t1.set_metadata("msgType", "accidentInfo")
        self.add_behaviour(self.HandleAccidentInfoBehaviour(agent=self), template=t1)
        t2 = Template()
        t2.set_metadata("msgType", "emergencyVehicleInfo")
        self.add_behaviour(
            self.HandleEmergencyVehicleInfoBehaviour(agent=self),
            template=t2,
        )
