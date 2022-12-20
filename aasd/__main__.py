import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template

from aasd.agents.manager_agent import ManagerAgent


class SenderAgent(Agent):
    class InformBehav(OneShotBehaviour):
        async def run(self):
            print("InformBehav running")
            msg = Message(to="manager@localhost")
            msg.set_metadata("performative", "inform")
            msg.set_metadata("msgType", "accidentInfo")
            msg.body = "Hello World"  # Set the message content

            await self.send(msg)
            print("Message sent!")

            msg = Message(to="manager@localhost")
            msg.set_metadata("performative", "inform")
            msg.set_metadata("msgType", "emergencyVehicleInfo")
            msg.body = (
                '{"x": 1.0, "y": 0.1, "assigned": false}'  # Set the message content
            )

            await self.send(msg)
            print("Message 2 sent!")

            # stop agent from behaviour
            await self.agent.stop()

    async def setup(self):
        print("SenderAgent started")
        b = self.InformBehav()
        self.add_behaviour(b)


if __name__ == "__main__":
    manager = ManagerAgent("manager@localhost", "passw0rd")
    manager.start().wait()
    sender = SenderAgent("admin@localhost", "passw0rd")
    sender.start().wait()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            manager.stop()
            sender.stop()
            break
    print("Agents finished")

#TODO inicjalizacja iluś agentów pojazdów, karetek i managera + dodać ich do docker-compose (na zasadzie participant1, karetka1 etc czy coś)
