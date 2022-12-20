import spade as spade

class TrafficParticipantAgent (spade.agent.Agent):
    #Rola TrafficParticipant
    class SendAccidentInfoToManagerBehaviour(spade.behaviour.OneShotBehaviour):
        async def run(self) -> None:

    class DisplayAlertBehaviour(spade.behaviour.OneShotBehaviour):
        async def run(self) -> None:

    class PropagateEmergencyVehicleInfoBehaviour(spade.behaviour.OneShotBehaviour):
        async def run(self) -> None:



    #Rola AccidentParticipant
