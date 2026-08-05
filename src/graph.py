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

    def get_connection_between_hub(self, hub1: Hub, hub2: Hub)\
            -> Connection | None:
        for connection in self.connections:
            if (connection.hub1 == hub1 and connection.hub2 == hub2) or (
                connection.hub1 == hub2 and connection.hub2 == hub1
            ):
                return connection
        return None
