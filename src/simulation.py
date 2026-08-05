from . import Graph, Hub, Visualizer, Connection, Pathfinder
import pygame


class Simulation:
    def __init__(self, graph: Graph) -> None:
        self.graph: Graph = graph
        self.pathfinder: Pathfinder = Pathfinder(self.graph)
        drones_path = self.pathfinder.find_shortest_path()
        if drones_path is None:
            raise ValueError("Error: It is impossible to reach the "
                             "end of the map")
        self.drones_path: list[Hub] = drones_path
        self.visualizer: Visualizer = Visualizer(self.graph)
        self.clock = pygame.time.Clock()
        self.clock_speed: int = 1

    def run(self) -> None:
        turn = 0
        time_passed = 0.0
        self.visualizer.render(turn)
        while any(
            True for drone in self.graph.drones
                if drone.location != self.graph.end
        ):
            time_per_tick = self.clock.tick(100) / 1000
            self.event_handler()
            time_passed += time_per_tick
            if time_passed >= 1 / self.clock_speed:
                time_passed = 0.0
                turn += 1
                self.update_drone_position()
                self.visualizer.render(turn)
        self.wait_for_close()

    def update_drone_position(self) -> None:
        for drone in self.graph.drones:
            if drone.location == self.graph.end:
                continue
            next_hub = self.drones_path[drone.nb_action + 1]
            if isinstance(drone.location, Connection):
                self.graph.update_location(drone, next_hub)
                drone.nb_action += 1
            elif next_hub.zone_type == "restricted":
                self.graph.move_to_hub_restricted(drone.location, next_hub,
                                                  drone)
            elif next_hub.zone_type != "restricted":
                self.graph.move_to_hub(drone.location, next_hub, drone)
        print("")
        for connection in self.graph.connections:
            connection.drone_taking_connection = 0

    def event_handler(self) -> None:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                pygame.quit()
                exit()
            if keys[pygame.K_UP]:
                if self.clock_speed < 60:
                    self.clock_speed += 1
            if keys[pygame.K_DOWN]:
                if self.clock_speed > 1:
                    self.clock_speed -= 1

    def wait_for_close(self) -> None:
        while True:
            self.clock.tick(100)
            self.event_handler()
