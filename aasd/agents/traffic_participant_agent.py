import spade as spade
import json as json
from spade.template import Template
from


class TrafficParticipantAgent(spade.agent.Agent):

    def __init__(self, vehicle, environment, *args, **kwargs):

        super(self).__init__(*args, **kwargs)

    def displayAlertBehaviour(self):
        print("Jedzie Karetka!")

    def propagateEmergencyVehicleInfoBehaviour(self, list):
        # wez pobliskie pojazdy od środowiska
        print("")

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
        self.informManagerAfterAccident(1, 2)
        t1 = Template()
        t1.set_metadata("msgType", "helpArrivalInfo")
        self.add_behaviour(self.WaitForProcessedAccidentInfoBehaviour, template=t1)

    class HandleForEmergencyVehicleIncomingBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            if msg:
                print("Emergency VehicleInfo received")

    class WaitForProcessedAccidentInfoBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            if msg:
                print("Help is arriving in: " + msg.body)

    # Rola AccidentParticipant

    async def setup(self):
        print(self.jid + " is starting")
        t1 = Template()
        t1.set_metadata("msgType", "evLocationData")
        self.add_behaviour(self.HandleForEmergencyVehicleIncomingBehaviour, template=t1)
