import pytest

import asyncio
import json
import spade

from aasd.environment import Environment, is_nearby
from aasd.vehicle import Vehicle, VehicleType as VT
from aasd.agents import TrafficParticipantAgent


@pytest.fixture
def default_environment_fixture():
    return Environment()


@pytest.fixture
def environment_with_vehicles():
    env = Environment()
    env.register_vehicle(Vehicle("ev1", 1100.0, 1100.0, vehicle_type=VT.Emergency))
    env.register_vehicle(Vehicle("ev2", 50.0, 50.0, vehicle_type=VT.Emergency))
    env.register_vehicle(Vehicle("tp1", 10.0, 10.0, vehicle_type=VT.Normal))
    env.register_vehicle(Vehicle("tp2", 1000.0, 1000.0, vehicle_type=VT.Normal))
    env.register_vehicle(Vehicle("tp3", 30.0, 30.0, vehicle_type=VT.Normal))
    env.register_vehicle(Vehicle("tp4", 100.0, 100.0, vehicle_type=VT.Normal))
    return env


@pytest.fixture
def vehicles_fixture():
    v1 = Vehicle("tp1", 100.0, 100.0, vehicle_type=VT.Normal)
    v2 = Vehicle("tp2", 150.0, 150.0, vehicle_type=VT.Normal)
    return v1, v2


@pytest.fixture
def vehicle_fixture():
    return Vehicle("tp1")


def test_initial_environment_has_no_vehicles(default_environment_fixture):
    assert len(default_environment_fixture.vehicles) == 0


def test_many_vehicles_register(default_environment_fixture):
    default_environment_fixture.register_vehicle(
        Vehicle(
            "tp1",
            *default_environment_fixture.get_random_coordinates(),
            vehicle_type=VT.Normal
        )
    )
    default_environment_fixture.register_vehicle(
        Vehicle(
            "tp2",
            *default_environment_fixture.get_random_coordinates(),
            vehicle_type=VT.Normal
        )
    )
    assert len(default_environment_fixture.vehicles) == 2


def test_single_vehicles_register(default_environment_fixture):
    default_environment_fixture.register_vehicle(
        Vehicle(
            "tp1",
            *default_environment_fixture.get_random_coordinates(),
            vehicle_type=VT.Normal
        )
    )
    assert len(default_environment_fixture.vehicles) == 1


def test_single_vehicle_unregister(environment_with_vehicles):
    assert len(environment_with_vehicles.vehicles) == 6
    vehicle = environment_with_vehicles.vehicles[0]
    environment_with_vehicles.unregister_vehicle(vehicle)
    assert len(environment_with_vehicles.vehicles) == 5


def test_many_vehicles_unregister(environment_with_vehicles):
    assert len(environment_with_vehicles.vehicles) == 6
    vehicle1 = environment_with_vehicles.vehicles[0]
    vehicle2 = environment_with_vehicles.vehicles[1]
    vehicle3 = environment_with_vehicles.vehicles[2]
    environment_with_vehicles.unregister_vehicle(vehicle1)
    environment_with_vehicles.unregister_vehicle(vehicle2)
    environment_with_vehicles.unregister_vehicle(vehicle3)
    assert len(environment_with_vehicles.vehicles) == 3


def test_get_emergency_vehicles(environment_with_vehicles):
    evs = environment_with_vehicles.get_emergency_vehicles()
    assert len(evs) == 2
    assert evs[0].id == "ev1"
    assert evs[1].id == "ev2"


def test_get_nearby_vehicles_success(environment_with_vehicles):
    tp1 = environment_with_vehicles.get_vehicle("tp1")
    nearby_vehicles = environment_with_vehicles.get_nearby_vehicles(tp1, 30.0)
    assert len(nearby_vehicles) == 1
    assert nearby_vehicles[0].id == "tp3"


def test_get_nearby_vehicles_fail(environment_with_vehicles):
    tp1 = environment_with_vehicles.get_vehicle("tp1")
    nearby_vehicles = environment_with_vehicles.get_nearby_vehicles(tp1, 20.0)
    assert len(nearby_vehicles) == 0


def test_make_random_accident(environment_with_vehicles):
    vehicles = environment_with_vehicles.vehicles
    types = [v.type for v in vehicles]
    assert VT.Crashed not in types
    environment_with_vehicles.make_random_accident()
    vehicles = environment_with_vehicles.vehicles
    types = [v.type for v in vehicles]
    assert VT.Crashed in types
    assert len([t for t in types if t == VT.Crashed]) == 1


def test_get_vehicle_success(environment_with_vehicles):
    assert environment_with_vehicles.get_vehicle("tp1")


def test_get_vehicle_fail(environment_with_vehicles):
    assert not environment_with_vehicles.get_vehicle("tp5")


def test_get_closest_emergency_vehicle(environment_with_vehicles):
    vehicle = environment_with_vehicles.get_vehicle("tp1")
    vehicle2 = environment_with_vehicles.get_vehicle("tp2")

    assert (
        environment_with_vehicles.get_closest_emergency_vehicle(vehicle.x, vehicle.y).id
        == "ev2"
    )
    assert (
        environment_with_vehicles.get_closest_emergency_vehicle(
            vehicle2.x, vehicle2.y
        ).id
        == "ev1"
    )


def test_vehicles_nearby_success(vehicles_fixture):
    assert is_nearby(*vehicles_fixture, 71.0)


def test_vehicles_nearby_fail(vehicles_fixture):
    assert not is_nearby(*vehicles_fixture, 70.0)


def test_reverse_direction(vehicle_fixture):
    assert vehicle_fixture.direction == 90.0
    vehicle_fixture.reverse_direction()
    assert vehicle_fixture.direction == 270.0


def test_toggle_movement(vehicle_fixture):
    assert vehicle_fixture.speed != 0
    vehicle_fixture.stop()
    assert vehicle_fixture.speed == 0
    vehicle_fixture.continue_moving()
    assert vehicle_fixture.speed != 0


def test_toggle_random_direction_change(vehicle_fixture):
    assert vehicle_fixture.random_direction_change_chance != 0
    vehicle_fixture.disable_random_direction_changes()
    assert vehicle_fixture.random_direction_change_chance == 0
    vehicle_fixture.enable_random_direction_changes()
    assert vehicle_fixture.random_direction_change_chance != 0


class DummySendListener(spade.agent.Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.received_messsages = []

    class ListenBehaviour(spade.behaviour.CyclicBehaviour):
        def __init__(self, agent, **kwargs):
            self.agent = agent
            super().__init__(**kwargs)

        async def run(self):
            msg = await self.receive()
            if msg:
                self.agent.received_messsages.append(msg)

    async def send_msg(self, message: spade.message.Message):
        await self.behaviour.send(message)

    async def setup(self):
        self.behaviour = self.ListenBehaviour(agent=self)
        self.add_behaviour(self.behaviour)


def test_propagate_ev_message():
    loop = asyncio.get_event_loop()

    env = Environment(object_size=20, chance_to_crash=0)
    agent = TrafficParticipantAgent(
        vehicle=Vehicle("tp1", 100.0, 100.0, vehicle_type=VT.Normal),
        env=env,
        jid="tp1@localhost",
        password="passw0rd",
    )

    dummy = DummySendListener(jid="dummy@localhost", password="passw0rd")

    loop.run_until_complete(asyncio.wait([agent.start(), dummy.start()]))

    msg = spade.message.Message(to="tp1")
    msg.set_metadata("msgType", "evLocationData")
    x, y = 110, 110
    msg.body = json.dumps({"x": x, "y": y, "direction": 0})

    loop.run_until_complete(dummy.send_msg(msg))
    loop.run_until_complete(asyncio.sleep(1))

    assert len(dummy.received_messsages) == 1
    msg = dummy.received_messsages[0]
    body = json.loads(msg.body)
    assert body["x"] == 110
    assert body["y"] == 110
    assert body["direction"] == 0
    assert body["ttl"] == 8
