from . import Graph, Hub, Visualizer, Connection, Pathfinder
import pygame

class Simulation:
    def __init__(self, graph: Graph) -> None:
        self.graph: Graph = graph
        self.pathfinder: Pathfinder = Pathfinder(self.graph)
        self.drones_path: list[Hub]|None = self.pathfinder.find_shortest_path()
        self.visualizer: Visualizer = Visualizer(self.graph)
        self.clock = pygame.time.Clock()
        if self.drones_path is None:
            raise ValueError("Error: It is impossible to reach the end of the map")
    
    def run(self) -> None:
        self.visualizer.draw_graph()
        turn = 0
        while(any(True for drone in self.graph.drones
                  if drone.location != self.graph.end)):
            turn += 1
            self.update_drone_position()
            self.event_handler()
            self.visualizer.render(turn)
            self.clock.tick(1)
        
    def update_drone_position(self) -> None:
        for drone in self.graph.drones:
            if drone.location == self.graph.end:
                continue
            next_hub = self.drones_path[drone.nb_action + 1]
            next_location = None
            if isinstance(drone.location, Connection):
                next_location = next_hub
            elif next_hub == self.graph.end:
                if self.graph.end.zone_type == "restricted":
                    next_location = self.graph.get_connection_between_hub(drone.location, next_hub)
                else:
                    next_location = next_hub
            elif next_hub.get_max_capacity() > next_hub.current_drone and\
                next_hub.zone_type != "restricted":
                next_location = next_hub
            elif next_hub.get_max_capacity() > next_hub.current_drone and\
                next_hub.zone_type == "restricted":
                next_location = self.graph.get_connection_between_hub(drone.location, next_hub)
            if next_location is None:
                continue
            print(f"D{drone.id}-{drone.location.get_name()}", end=" ")
            self.graph.update_location(drone, next_location)
            if isinstance(next_location, Hub):
                drone.nb_action += 1
            print(f"D{drone.id}-{drone.location.get_name()}")
    
    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

