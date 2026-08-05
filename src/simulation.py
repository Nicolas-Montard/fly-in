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
        self.visualizer.draw_graph()
        turn = 0
        time_passed = 0.0
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
            next_location: Hub | Connection | None = None
            if isinstance(drone.location, Connection):
                next_location = next_hub
            elif next_hub == self.graph.end:
                if self.graph.end.zone_type == "restricted":
                    next_location = self.graph.get_connection_between_hub(
                        drone.location, next_hub
                    )
                else:
                    next_location = next_hub
            elif (
                next_hub.get_max_capacity() > next_hub.current_drone
                and next_hub.zone_type != "restricted"
            ):
                next_location = next_hub
            elif next_hub.zone_type == "restricted":
                connection = self.graph.get_connection_between_hub(
                    drone.location, next_hub
                )
                if connection is None:
                    raise ValueError(
                        "An error as occured in update drone:\
                                     unable to find connection between hub"
                    )
                if connection.current_drone < connection.get_max_capacity():
                    next_location = connection
            if next_location is None:
                continue
            print(f"D{drone.id}-{drone.location.get_name()}", end=" ")
            self.graph.update_location(drone, next_location)
            if isinstance(next_location, Hub):
                drone.nb_action += 1
            print(f"D{drone.id}-{drone.location.get_name()}")

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
