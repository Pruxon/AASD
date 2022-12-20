import spade as spade

class ManagerAgent(spade.agent.Agent):
    class ListenForAccidentsBehaviour(spade.behaviour.CyclicBehaviour):
        async def on_start(self) -> None:
            print("Manager is starting to hear for accident info")

        async def run(self):
            




    async def setup(self) -> None:
        print("Manager is starting")
