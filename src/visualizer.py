from . import Graph, Hub, Connection
import pygame


class Visualizer:
    """Renders a Graph and its drones to a pygame window.
 
    Scales the graph's map coordinates to fit and center within a
    fixed-size window, then draws connections, hubs, and drones each
    frame.
 
    Attributes:
        graph: The graph to render.
        screen: The pygame display surface.
        padding: Minimum margin, in pixels, kept around the graph.
        font: Font used for hub names and the turn counter.
        small_font: Smaller font used for drone labels.
        min_x: Smallest hub x coordinate in the graph.
        max_x: Largest hub x coordinate in the graph.
        min_y: Smallest hub y coordinate in the graph.
        max_y: Largest hub y coordinate in the graph.
        scale_x: Pixels per unit of x coordinate.
        scale_y: Pixels per unit of y coordinate.
        offset_x: Horizontal pixel offset applied to center the graph.
        offset_y: Vertical pixel offset applied to center the graph.
    """
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
        """Compute the scale and offset needed to fit and center the graph.
 
        Determines the coordinate bounds of all hubs, derives a
        pixels-per-unit scale for each axis that fits the graph within
        the window (minus padding), and computes the offset needed to
        center the scaled graph within the available space.
 
        Args:
            width: Width of the target window, in pixels.
            height: Height of the target window, in pixels.
        """
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
        """Convert a hub's map coordinates into screen pixel coordinates.
 
        Args:
            x: The map x coordinate.
            y: The map y coordinate.
 
        Returns:
            The corresponding (pixel_x, pixel_y) position on screen.
        """
        scaled_x = self.offset_x + ((x - self.min_x) * self.scale_x)
        scaled_y = self.offset_y + ((y - self.min_y) * self.scale_y)
        return (int(scaled_x), int(scaled_y))

    def draw_graph(self) -> None:
        """Draw connections, hubs, and drones, in that order (back to front)."""
        self.draw_connection()
        self.draw_hubs()
        self.draw_drones()

    def draw_connection(self) -> None:
        """Draw a line for every connection in the graph."""
        for conn in self.graph.connections:
            hub1_pos = self.scale_value(conn.hub1.x, conn.hub1.y)
            hub2_pos = self.scale_value(conn.hub2.x, conn.hub2.y)
            pygame.draw.line(self.screen, (0, 0, 0), hub1_pos, hub2_pos, 2)

    def draw_hubs(self) -> None:
        """Draw every hub as a colored circle with its name above it.
 
        Falls back to black if a hub's color isn't a valid pygame color.
        """
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
        """Draw every drone as a small polygon with its id label.
 
        Drones on a hub are centered on that hub; drones on a
        connection are centered on the connection's midpoint. A small
        per-drone offset is applied so drones sharing the same
        location don't fully overlap.
        """
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
                center = ((x1 + x2) // 2) + offset, ((y1 + y2) // 2) + offset
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
        """Draw a small diamond-shaped polygon centered at a point.
 
        Falls back to red if `color` isn't a valid pygame color.
 
        Args:
            center: Pixel coordinates of the polygon's center.
            size: Distance, in pixels, from the center to each point
                of the diamond.
            color: Fill color for the polygon.
        """
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
        """Clear the screen and draw a full frame for the given turn.
 
        Args:
            turn_number: The current simulation turn, shown on screen.
        """
        self.screen.fill((255, 255, 255))
        self.draw_graph()
        turn_counter = self.font.render(f"Turn {turn_number}", True, (0, 0, 0))
        self.screen.blit(
            turn_counter,
            (self.screen.get_width() // 2, self.screen.get_height() - 20)
        )
        pygame.display.update()
