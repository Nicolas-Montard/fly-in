from pydantic import BaseModel
from . import Hub, Drone, Connection

class Visual(BaseModel):
    hubs: list[Hub]
    drones: list[Drone]
    connections: list[Connection]

    