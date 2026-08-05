from pydantic import BaseModel
from . import Hub, Connection


class Drone(BaseModel):
    """A drone moving through the graph, from the start hub to the end hub.

    Attributes:
        location: The drone's current position, either a Hub (when it
            occupies a zone) or a Connection (when it is mid-traversal,
            typically while crossing a restricted zone over two turns).
        nb_action: Number of hubs reached so far along its path, used
            as an index into the precomputed shortest path.
        id: Unique identifier of the drone.
    """
    location: Hub | Connection
    nb_action: int = 0
    id: int
