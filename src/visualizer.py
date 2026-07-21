from . import Graph, Hub, Connection
import pygame
from sys import exit

class Visualizer():
    def __init__(self, graph: Graph, width: int=900, height: int=700, padding: int=60) -> None:
        pygame.init()
        self.graph: Graph = graph
        self.screen = pygame.display.set_mode((width, height))
        self.padding = padding
        self.font = pygame.font.Font(None, 20)
        self.calculate_size_of_graph(width, height)

    def calculate_size_of_graph(self, width: int, height: int) -> None:
        x_coordinates = [hub.x for hub in self.graph.hubs]
        y_coordinates = [hub.y for hub in self.graph.hubs]
        self.min_x = min(x_coordinates)
        self.max_x = max(x_coordinates)
        self.min_y = min(y_coordinates)
        self.max_y = max(y_coordinates)
        self.scale_x = (width - 2 * self.padding) / max(1, self.max_x - self.min_x)
        self.scale_y = (height - 2 * self.padding) / max(1, self.max_y - self.min_y)

    def scale_value(self, x: int, y: int) -> tuple:
        scaled_x = self.padding + ((x - self.min_x) * self.scale_x)
        scaled_y = self.padding + ((y - self.min_y) * self.scale_y)
        return (int(scaled_x), int(scaled_y))
    
    def draw_graph(self):
        self.draw_connection()
        self.draw_hubs()
        self.draw_drones()
    
    def draw_connection(self) -> None:
        for conn in self.graph.connections:
            hub1_pos = self.scale_value(conn.hub1.x, conn.hub1.y)
            hub2_pos = self.scale_value(conn.hub2.x, conn.hub2.y)
            pygame.draw.line(self.screen, (0, 0, 0), hub1_pos, hub2_pos, 2)
    
    def draw_hubs(self) -> None:
        for hub in self.graph.hubs:
            position = self.scale_value(hub.x, hub.y)
            try:
                pygame.draw.circle(self.screen, hub.color, position, 18)
            except ValueError:
                pygame.draw.circle(self.screen, "black", position, 18)
            hub_name = self.font.render(hub.name, True, (0, 0, 0))
            self.screen.blit(hub_name, (position[0] - (hub_name.get_width() // 2), position[1] - 10))
    
    def draw_drones(self) -> None:
        for drone in self.graph.drones:
            if isinstance(drone.location, Hub):
                position = self.scale_value(drone.location.x, drone.location.y)
                offset = (drone.id % 5) * 6
                center = (position[0] + offset, position[1] + offset)
                self.draw_polygon(center, 7, "green")
                drone_name = self.font.render(f"D{drone.id}", True, (0, 0, 0))
                self.screen.blit(drone_name, (position[0] - (drone_name.get_width() // 2),
                                              position[1] - (drone_name.get_height() // 2)))
            elif isinstance(drone.location, Connection):
                x1, y1 = drone.location.hub1.x, drone.location.hub1.y
                x2, y2 = drone.location.hub2.x, drone.location.hub2.y
                position = self.scale_value((x1 + x2) // 2, (y1 + y2) // 2)
                self.draw_polygon(position, 7, "green")
                drone_name = self.font.render(f"D{drone.id}", True, (0, 0, 0))
                self.screen.blit(drone_name, (position[0] - (drone_name.get_width() // 2),
                                              position[1] - (drone_name.get_height() // 2)))
                
    
    def draw_polygon(self, center, size, color):
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
    
    def render(self, turn_number):
        self.screen.fill((255, 255, 255))
        self.draw_graph()
        turn_counter = self.font.render(f"Turn {turn_number}", True, (255, 255, 255))
        self.screen.blit(turn_counter, (self.screen.get_width() // 2,
                                        self.screen.get_height() - 20))
        pygame.display.update()
