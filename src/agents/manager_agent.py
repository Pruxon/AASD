import spade as spade

class ManagerAgent(spade.agent.Agent):
    class ListenForAccidentsBehaviour(spade.behaviour.CyclicBehaviour):
        async def on_start(self) -> None:
            print("Manager is listening for accident info")

        async def run(self):
            msg = await self.receive(timeout=1)

    class ListenForEmergencyVehicleInfoBehaviour(spade.behaviour.CyclicBehaviour):
        async def on_start(self) -> None:
            print("Manager is listening for emergency vehicle info")

    class SendAccidentInfoProccessedBehaviour(spade.behaviour.OneShotBehaviour):
        async def run(self) -> None:


    class SendAccidentInfoToEmergencyVehicleBehaviour(spade.behaviour.OneShotBehaviour):
        async def run(self) -> None:



    async def setup(self) -> None:
        print("Manager is starting")
