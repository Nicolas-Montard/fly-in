from pydantic import BaseModel
from . import Hub, Connection

class Drone(BaseModel):
    location: Hub|Connection
    id: int