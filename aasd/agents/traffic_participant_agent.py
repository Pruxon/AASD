import asyncio
import spade as spade
import json as json
from spade.template import Template
from aasd.environment import Vehicle, Environment


class TrafficParticipantAgent(spade.agent.Agent):

    def __init__(self, vehicle: Vehicle, env: Environment, *args, **kwargs):
        self.vehicle = vehicle
        self.env = env
        self.helpDispatched = False
        super(self).__init__(*args, **kwargs)

    def displayAlertBehaviour(self):
        print("Jedzie Karetka!")

    def propagateEmergencyVehicleInfo(self, message: spade.message.Message):
        nearby_vehicles = self.env.get_nearby_vehicles(self.vehicle, 5)
        for vehicle in nearby_vehicles:
            msg = spade.message.Message(to=vehicle.id)
            msg.set_metadata("msgType", "emergencyVehicleInfo")
            msg.body = message.body
            await self.send(msg)

    def createAccidentMessagebody(self, x: float, y: float) -> str:
        dictionary = {'X': x, 'Y': y, 'message': "Accident happened, help needed"}
        return json.dumps(dictionary)

    def informManagerAfterAccident(self, x: float, y: float):
        msg = spade.message.Message(to="manager@localhost")
        msg.set_metadata("performative", "inform")
        msg.set_metadata("msgType", "accidentInfo")
        msg.body = self.createAccidentMessagebody(x, y)
        await self.send(msg)

    def accidentHappened(self):
        self.helpDispatched = False
        self.add_behaviour(self.InformManagerBehaviour(agent=self))

    class InformManagerBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def run(self):
            if self.agent.helpDispatched:
                self.kill()
            else:
                self.agent.informManagerAfterAccident(self.agent.vehicle.x, self.agent.vehicle.y)
                await asyncio.sleep(1)

    class HandleForEmergencyVehicleIncomingBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def run(self):
            msg = await self.receive()
            if msg:
                self.agent.propagateEmergencyVehicleInfo(self=self.agent, message=msg)

    class HandleHelpArrivalInfoBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def run(self):
            msg = await self.receive()
            if msg:
                print("Help is arriving in: " + msg.body)
                self.agent.helpDispatched = True


    async def setup(self):
        print(self.jid + " is starting")
        t1 = Template()
        t1.set_metadata("msgType", "evLocationData")
        self.add_behaviour(self.HandleForEmergencyVehicleIncomingBehaviour(agent=self), template=t1)
        t2 = Template()
        t2.set_metadata("msgType", "helpArrivalInfo")
        self.add_behaviour(self.HandleHelpArrivalInfoBehaviour(agent=self), template=t2)
