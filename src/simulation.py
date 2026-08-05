from . import Graph, Hub, Visualizer, Connection, Pathfinder
import pygame


class Simulation:
    """Runs the drone simulation on a graph, with a pygame visual loop.

    Computes the shortest path once at startup, then advances all
    drones along it turn by turn, rendering the graph after each turn
    and letting the user adjust simulation speed or quit at any time.
    Once every drone has reached the end, the window is kept open
    until the user closes it.

    Attributes:
        graph: The graph the simulation runs on.
        pathfinder: Used to compute the shared shortest path all
            drones follow.
        drones_path: The precomputed shortest path from start to end,
            as an ordered list of hubs.
        visualizer: Handles rendering the graph and drones to screen.
        clock: Pygame clock used to cap the frame rate and measure
            elapsed time.
        clock_speed: Number of simulation turns advanced per second.
    """

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
        """Run the main simulation loop until every drone reaches the end.

        Advances the simulation at a rate of `clock_speed` turns per
        second, independently of the display's frame rate, so input
        (speed changes, quitting) stays responsive regardless of how
        fast the simulation itself is running. Keeps the window open
        after completion via `wait_for_close`.
        """
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
        """Advance every drone one step along its shared shortest path.

        Drones already on a connection move onto their target hub.
        Drones on a hub move toward their next hub directly, or via
        the connecting connection first if that hub is restricted
        (which costs an extra turn). Resets each connection's
        per-turn traversal count at the end of the turn.
        """
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
        """Process pygame events and held keys.

        Quits the program on window close or Escape. Adjusts
        `clock_speed` up or down while the Up/Down arrow keys are
        held, within the range [1, 60].
        """
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
        """Keep the window open and responsive after the simulation ends.

        Loops indefinitely, only processing events (so the user can
        still quit), without advancing the simulation further.
        """
        while True:
            self.clock.tick(100)
            self.event_handler()
