import requests

from dataclasses import dataclass
from aasd.enums import AgentType


@dataclass
class AgentData:
    user: str
    type: AgentType
    host: str = "localhost"
    password: str = "passw0rd"

    def jid_str(self) -> str:
        return self.user + "@" + self.host


def register_users_to_ejabberd(users: list[AgentData]):
    url = "http://localhost:5443/api/register"
    for u in users:
        data = {"user": u.user, "host": u.host, "password": u.password}
        requests.post(url, json=data, auth=("admin@localhost", "passw0rd"))
