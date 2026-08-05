from . import Graph, Hub, Connection
import pygame


class Visualizer:
    def __init__(
        self, graph: Graph,
        width: int = 1500,
        height: int = 1000,
        padding: int = 60
    ) -> None:
        pygame.init()
        self.graph: Graph = graph
        self.screen = pygame.display.set_mode((width, height))
        self.padding = padding
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 12)
        self.calculate_size_of_graph(width, height)

    def calculate_size_of_graph(self, width: int, height: int) -> None:
        x_coordinates = [hub.x for hub in self.graph.hubs.values()]
        y_coordinates = [hub.y for hub in self.graph.hubs.values()]
        self.min_x = min(x_coordinates)
        self.max_x = max(x_coordinates)
        self.min_y = min(y_coordinates)
        self.max_y = max(y_coordinates)
        self.scale_x = (width - 2 * self.padding) / \
            max(1, self.max_x - self.min_x)
        self.scale_y = (height - 2 * self.padding) / \
            max(1, self.max_y - self.min_y)

        graph_width = (self.max_x - self.min_x) * self.scale_x
        graph_height = (self.max_y - self.min_y) * self.scale_y
        self.offset_x = self.padding + \
            (width - 2 * self.padding - graph_width) / 2
        self.offset_y = self.padding + \
            (height - 2 * self.padding - graph_height) / 2

    def scale_value(self, x: int, y: int) -> tuple:
        scaled_x = self.offset_x + ((x - self.min_x) * self.scale_x)
        scaled_y = self.offset_y + ((y - self.min_y) * self.scale_y)
        return (int(scaled_x), int(scaled_y))

    def draw_graph(self) -> None:
        self.draw_connection()
        self.draw_hubs()
        self.draw_drones()

    def draw_connection(self) -> None:
        for conn in self.graph.connections:
            hub1_pos = self.scale_value(conn.hub1.x, conn.hub1.y)
            hub2_pos = self.scale_value(conn.hub2.x, conn.hub2.y)
            pygame.draw.line(self.screen, (0, 0, 0), hub1_pos, hub2_pos, 2)

    def draw_hubs(self) -> None:
        for hub in self.graph.hubs.values():
            position = self.scale_value(hub.x, hub.y)
            try:
                pygame.draw.circle(self.screen, hub.color, position, 18)
            except ValueError:
                pygame.draw.circle(self.screen, "black", position, 18)
            hub_name = self.font.render(hub.name, True, (0, 0, 0))
            self.screen.blit(
                hub_name,
                (
                    position[0] - (hub_name.get_width() // 2),
                    position[1] - 18 - hub_name.get_height() - 2,
                ),
            )

    def draw_drones(self) -> None:
        for drone in self.graph.drones:
            offset = (drone.id % 3) * 4
            if isinstance(drone.location, Hub):
                position = self.scale_value(drone.location.x, drone.location.y)
                center = (position[0] + offset, position[1] + offset)
            elif isinstance(drone.location, Connection):
                x1, y1 = self.scale_value(
                    drone.location.hub1.x, drone.location.hub1.y)
                x2, y2 = self.scale_value(
                    drone.location.hub2.x, drone.location.hub2.y)
                center = ((x1 + x2) // 2), ((y1 + y2) // 2)
            else:
                continue

            self.draw_polygon(center, 9, "green")
            drone_name = self.small_font.render(
                f"D{drone.id}", True, (0, 0, 0))
            self.screen.blit(
                drone_name,
                (
                    center[0] - (drone_name.get_width() // 2),
                    center[1] - (drone_name.get_height() // 2),
                ),
            )

    def draw_polygon(self,
                     center: tuple[int, int],
                     size: int,
                     color: str) -> None:
        x, y = center
        points = [
            (x, y - size),
            (x + size, y),
            (x, y + size),
            (x - size, y),
        ]
        try:
            pygame.draw.polygon(self.screen, color, points)
        except ValueError:
            pygame.draw.polygon(self.screen, "red", points)

    def render(self, turn_number: int) -> None:
        self.screen.fill((255, 255, 255))
        self.draw_graph()
        turn_counter = self.font.render(f"Turn {turn_number}", True, (0, 0, 0))
        self.screen.blit(
            turn_counter,
            (self.screen.get_width() // 2, self.screen.get_height() - 20)
        )
        pygame.display.update()
