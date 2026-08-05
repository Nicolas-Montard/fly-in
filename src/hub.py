from pydantic import BaseModel, Field
from typing import Literal

ZoneType = Literal["normal", "blocked", "restricted", "priority"]
"""Valid zone types a hub can have, each affecting movement cost and rules."""


class Hub(BaseModel):
    """A zone on the map that drones can occupy or pass through.

    Represents a single node in the graph, identified by its name and
    position, with a zone type that determines movement cost and any
    special traversal rules (e.g. restricted zones require an extra
    turn via an intermediate connection).

    Attributes:
        x: Horizontal coordinate of the hub on the map.
        y: Vertical coordinate of the hub on the map.
        name: Unique name identifying the hub.
        zone_type: The kind of zone this hub represents. Defaults to "normal".
        color: Display color used for visual representation. Defaults to "black".
        max_drones: Maximum number of drones allowed to occupy this hub
            simultaneously. Ignored for the start and end hubs. Defaults to 1.
        current_drone: Number of drones currently occupying this hub.
        explored: Whether this hub has been visited by the pathfinder.
    """
    x: int
    y: int
    name: str
    zone_type: ZoneType = Field(default="normal")
    color: str = Field(default="black")
    max_drones: int = Field(default=1, ge=0)
    current_drone: int = 0
    explored: bool = False

    def get_name(self) -> str:
        """Return the hub's name."""
        return self.name

    def get_max_capacity(self) -> int:
        """Return the maximum number of drones this hub can hold at once."""
        return self.max_drones
