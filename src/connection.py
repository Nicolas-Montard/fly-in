from pydantic import BaseModel, Field
from . import Hub


class Connection(BaseModel):
    """Bidirectional link between two hubs, allowing drones to travel between them.

    A connection is used both as a direct edge in the graph and as an
    intermediate location for drones crossing a restricted zone (which
    costs an extra turn to traverse).

    Attributes:
        hub1: One endpoint of the connection.
        hub2: The other endpoint of the connection.
        max_link_capacity: Maximum number of drones allowed to traverse
            this connection simultaneously. Defaults to 1.
        current_drone: Number of drones currently occupying this connection.
        drone_taking_connection: Number of drones that traverse this connection
        in one turn.
    """
    hub1: Hub
    hub2: Hub
    max_link_capacity: int = Field(default=1, ge=0)
    current_drone: int = 0
    drone_taking_connection: int = 0

    def get_name(self) -> str:
        """Return the connection's display name as 'hub1-hub2'."""
        return f"{self.hub1.name}-{self.hub2.name}"

    def get_max_capacity(self) -> int:
        """Return the maximum number of drones this connection can hold at once."""
        return self.max_link_capacity
