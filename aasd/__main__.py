from tkinter import mainloop
from collections import namedtuple

from aasd.environment import Environment
from aasd.gui import MovementSimulationWindow
from aasd.vehicle import Vehicle, VehicleType
from aasd.agents import ManagerAgent, TrafficParticipantAgent, EmergencyVehicleAgent
from aasd.ejabberd_register import register_users_to_ejabberd, AgentData, AgentType


InitialAgentData = namedtuple('InitialAgentData', 'name type')


def create_agent(agent_data: AgentData, environment: Environment):
    if agent_data.type is AgentType.EmergencyVehicle:
        vehicle = Vehicle(
            agent_data.jid_str(), *environment.get_random_coordinates(), vehicle_type=VehicleType.Emergency
        )
        environment.register_vehicle(vehicle)
        agent = EmergencyVehicleAgent(
            vehicle=vehicle, env=environment, jid=agent_data.jid_str(), password=agent_data.password
        )
        agent.start()
    elif agent_data.type is AgentType.Manager:
        agent = ManagerAgent(env=environment, jid=agent_data.jid_str(), password=agent_data.password)
        agent.start()
    elif agent_data.type is AgentType.TrafficParticipant:
        vehicle = Vehicle(
            agent_data.jid_str(), *environment.get_random_coordinates(), vehicle_type=VehicleType.Normal
        )
        environment.register_vehicle(vehicle)
        agent = TrafficParticipantAgent(
            vehicle=vehicle,
            env=environment,
            jid=agent_data.jid_str(),
            password=agent_data.password,
        )
        agent.start()


if __name__ == "__main__":
    env = Environment()

    initial_agents_data = [
        InitialAgentData('manager', AgentType.Manager),
        InitialAgentData('ev1', AgentType.EmergencyVehicle),
        InitialAgentData('ev2', AgentType.EmergencyVehicle),
        InitialAgentData('tp1', AgentType.TrafficParticipant),
        InitialAgentData('tp2', AgentType.TrafficParticipant),
        InitialAgentData('tp3', AgentType.TrafficParticipant),
        InitialAgentData('tp4', AgentType.TrafficParticipant),
    ]

    agents_data = [AgentData(data.name, data.type) for data in initial_agents_data]

    # Rejestrowanie agentów na serwerze XMPP
    register_users_to_ejabberd(agents_data)

    for item in agents_data:
        create_agent(item, env)

    simulation = MovementSimulationWindow(env)
    simulation.start()

    mainloop()
