from . import Connection, Hub, Drone

class Graph:
    def __init__(self):
        self.hubs: list[Hub] = []
        self.connections: list[Connection] = []
        self.drones: list[Drone] = []
        self.start: Hub
        self.end: Hub

    def add_hub(self, hub: Hub):
        self.hubs.append(hub)

    def add_connection(self, connection: Connection):
        self.connections.append(connection)

    def get_neighbors(self, hub: Hub):
        result: list[Hub] = []
        for connection in self.connections:
            if connection.hub1 == hub:
                result.append((connection.hub2, connection))
            elif connection.hub2 == hub:
                result.append((connection.hub1, connection))
        return result

    def get_hub(self, name):
        return self.hubs[name]