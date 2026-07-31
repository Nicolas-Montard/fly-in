from . import Graph, Hub, Visualizer, Connection
import pygame

class Simulation:
    def __init__(self, graph: Graph) -> None:
        self.graph: Graph = graph
        # TODO Call calculate drone path.
        self.drones_path: dict[int, list[Hub|Connection]] = {}
        self.visualizer: Visualizer = Visualizer(self.graph)
        self.clock = pygame.time.Clock()
    
    def run(self) -> None:
        self.visualizer.draw_graph()
        while(any(True for drone in self.graph.drones
                  if drone.location != self.graph.end)):
            self.update_drone_position()
            self.visualizer.draw_graph()
            self.clock.tick(1)
        
    def update_drone_position(self) -> None:
        for i, drone in enumerate(self.graph.drones):
            if drone.location == self.graph.end:
                continue
            print(f"D{drone.id}-{drone.location.get_name()}", end=" ")
            self.graph.update_location(drone, self.drones_path[i].pop(-1))
            print(f"D{drone.id}-{drone.location.get_name()}")
    
    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

