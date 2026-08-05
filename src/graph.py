from . import Connection, Hub, Drone


class Graph:
    def __init__(self) -> None:
        self.hubs: dict[str, Hub] = {}
        self.connections: list[Connection] = []
        self.drones: list[Drone] = []
        self.start: Hub
        self.end: Hub

    def add_hub(self, hub: Hub) -> None:
        self.hubs[hub.name] = hub

    def add_connection(self, connection: Connection) -> None:
        self.connections.append(connection)

    def get_neighbors(self, hub: Hub) -> list[tuple[Hub, Connection]]:
        result: list[tuple[Hub, Connection]] = []
        for connection in self.connections:
            if connection.hub1 == hub:
                result.append((connection.hub2, connection))
            elif connection.hub2 == hub:
                result.append((connection.hub1, connection))
        return result

    def get_hub(self, name: str) -> Hub:
        return self.hubs[name]

    def update_location(self, drone: Drone, location: Connection | Hub)\
            -> None:
        drone.location.current_drone -= 1
        drone.location = location
        drone.location.current_drone += 1
        print(f"D{drone.id}-{drone.location.get_name()}")

    def get_connection_between_hub(self, hub1: Hub, hub2: Hub)\
            -> Connection | None:
        for connection in self.connections:
            if (connection.hub1 == hub1 and connection.hub2 == hub2) or (
                connection.hub1 == hub2 and connection.hub2 == hub1
            ):
                return connection
        return None

    def move_to_hub(self, hub1: Hub, hub2: Hub, drone: Drone) -> None:
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

        

        
