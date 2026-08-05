from pydantic import BaseModel
from . import Hub, Connection


class Drone(BaseModel):
    location: Hub | Connection
    nb_action: int = 0
    id: int
