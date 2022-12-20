import spade as spade
from spade.template import Template


class ManagerAgent(spade.agent.Agent):
    class HandleAccidentInfoBehaviour(spade.behaviour.CyclicBehaviour):
        async def on_start(self) -> None:
            print("Manager is listening for accident info...")

        async def run(self):
            msg = await self.receive()
            if msg:
                print(f"Message AccidentInfo received:\n{msg}")
                print(msg.sender)
                print(msg.get_metadata("performative"))

    class HandleEmergencyVehicleInfoBehaviour(spade.behaviour.CyclicBehaviour):
        async def on_start(self) -> None:
            print("Manager is listening for emergency vehicle info...")

        async def run(self):
            msg = await self.receive()
            if msg:
                print(f"Message EmergencyVehicleInfo received:\n{msg}")
                print(msg.sender)
                print(msg.get_metadata("performative"))

    async def setup(self) -> None:
        print("Manager is starting")
        self.emergency_vehicles = []

        t1 = Template()
        t1.set_metadata("msgType", "accidentInfo")
        self.add_behaviour(self.HandleAccidentInfoBehaviour(), template=t1)
        t2 = Template()
        t2.set_metadata("msgType", "evLocationData")
        self.add_behaviour(self.HandleEmergencyVehicleInfoBehaviour(), template=t2)
