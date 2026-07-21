from . import Graph, Hub, Connection
import copy

class Pathfinder():
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
    
    def get_drones_path(self) -> dict[int, list[Hub|Connection]]:
        self.drone_path: dict[int, list[Hub|Connection]] = {}
        for i in range(len(self.graph.drones)):
            self.drone_path[i] = []
    
    def get_one_drone_path(self) -> list[Hub|Connection]:
        path_to_explore: list[Hub] = []
        neighbors = self.graph.get_neighbors(self.graph.start)
        for neigbor in neighbors:
            if neigbor not in path_explored:
                path_to_explore() 

