from . import Connection, Hub, Drone


class Graph:
    """Represents the map as a graph of hubs connected by bidirectional links.

    Holds all hubs, connections, and drones for a given simulation, and
    provides the operations needed to navigate and move drones through
    the graph (including the two-turn handling of restricted zones).

    Attributes:
        hubs: All hubs in the graph, indexed by name.
        connections: All connections (edges) in the graph.
        drones: All drones currently active in the simulation.
        start: The start hub of the map.
        end: The end hub (goal) of the map.
    """
    def __init__(self) -> None:
        self.hubs: dict[str, Hub] = {}
        self.connections: list[Connection] = []
        self.drones: list[Drone] = []
        self.start: Hub
        self.end: Hub

    def add_hub(self, hub: Hub) -> None:
        """Register a hub in the graph, indexed by its name."""
        self.hubs[hub.name] = hub

    def add_connection(self, connection: Connection) -> None:
        """Register a connection (edge) in the graph."""
        self.connections.append(connection)

    def get_neighbors(self, hub: Hub) -> list[tuple[Hub, Connection]]:
        """Return every hub directly reachable from the given hub.

        Args:
            hub: The hub to look up neighbors for.

        Returns:
            A list of (neighbor_hub, connection) pairs for each
            connection involving `hub`.
        """
        result: list[tuple[Hub, Connection]] = []
        for connection in self.connections:
            if connection.hub1 == hub:
                result.append((connection.hub2, connection))
            elif connection.hub2 == hub:
                result.append((connection.hub1, connection))
        return result

    def get_hub(self, name: str) -> Hub:
        """Return the hub registered under the given name."""
        return self.hubs[name]

    def update_location(self, drone: Drone, location: Connection | Hub)\
            -> None:
        """Move a drone to a new location, updating occupancy counts.

        Decrements the occupancy count of the drone's current location,
        assigns the new location, and increments its occupancy count.

        Args:
            drone: The drone being moved.
            location: The hub or connection the drone is moving to.
        """
        drone.location.current_drone -= 1
        drone.location = location
        drone.location.current_drone += 1
        print(f"D{drone.id}-{drone.location.get_name()}")

    def get_connection_between_hub(self, hub1: Hub, hub2: Hub)\
            -> Connection | None:
        """Return the connection linking two hubs, regardless of order.

        Args:
            hub1: One of the two hubs.
            hub2: The other hub.

        Returns:
            The matching Connection, or None if no connection links
            `hub1` and `hub2`.
        """
        for connection in self.connections:
            if (connection.hub1 == hub1 and connection.hub2 == hub2) or (
                connection.hub1 == hub2 and connection.hub2 == hub1
            ):
                return connection
        return None

    def move_to_hub(self, hub1: Hub, hub2: Hub, drone: Drone) -> None:
        """Move a drone directly from hub1 to hub2 (normal/priority zones).

        Does nothing if hub2 is already at full capacity, or if the
        connection between the two hubs is already at full capacity.

        Args:
            hub1: The drone's current hub.
            hub2: The destination hub.
            drone: The drone being moved.

        Raises:
            ValueError: If no connection exists between hub1 and hub2.
        """
        if hub2.current_drone >= hub2.get_max_capacity() and hub2 != self.end:
            return
        connection = self.get_connection_between_hub(hub1, hub2)
        if connection is None:
            raise ValueError(
                "An error as occured in update drone:\
                            unable to find connection between hub"
            )
        if connection.drone_taking_connection >= connection.get_max_capacity():
            return
        connection.drone_taking_connection += 1
        self.update_location(drone, hub2)
        drone.nb_action += 1

    def move_to_hub_restricted(self, hub1: Hub, hub2: Hub, drone: Drone):
        """Start moving a drone toward a restricted destination hub.

        Places the drone onto the connection between hub1 and hub2 as
        the first of two turns needed to cross into a restricted zone,
        provided the connection and destination hub have room.

        Args:
            hub1: The drone's current hub.
            hub2: The restricted destination hub.
            drone: The drone being moved.

        Raises:
            ValueError: If no connection exists between hub1 and hub2.
        """
        connection = self.get_connection_between_hub(hub1, hub2)
        if connection is None:
            raise ValueError(
                "An error as occured in update drone:\
                            unable to find connection between hub"
            )
        if connection.drone_taking_connection >= connection.get_max_capacity():
            return
        if (connection.drone_taking_connection + hub2.current_drone) >= \
            hub2.get_max_capacity() and hub2 != self.end \
            and hub2.current_drone == 0:
            return
        if (connection.drone_taking_connection + hub2.current_drone) >= \
            hub2.get_max_capacity() + 1 and hub2 != self.end:
            return
        self.update_location(drone, connection)
        connection.drone_taking_connection += 1
