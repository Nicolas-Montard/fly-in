from . import Graph, Hub


class Pathfinder:
    ZONE_COST = {
        "normal": 1,
        "priority": 0.99,
        "restricted": 2,
    }

    def __init__(self, graph: Graph) -> None:
        self.graph: Graph = graph

    def find_shortest_path(self) -> list[Hub] | None:
        distances_from_start: dict[str, float] = {
            name: float("inf") for name in self.graph.hubs
        }
        distances_from_start[self.graph.start.name] = 0
        previous_hub: dict[str, str] = {}
        unvisited: set[str] = set(self.graph.hubs.keys())

        while unvisited:
            current_name = self.find_closest_unvisited(distances_from_start,
                                                       unvisited)
            if current_name is None or \
                    distances_from_start[current_name] == float("inf"):
                return None
            if current_name is None:
                break
            if current_name == self.graph.end.name:
                return self.recreate_path(
                    previous_hub, self.graph.start.name, self.graph.end.name
                )

            unvisited.remove(current_name)
            current_hub = self.graph.get_hub(current_name)

            for neighbor, connection in self.graph.get_neighbors(current_hub):
                if neighbor.zone_type == "blocked":
                    continue
                if neighbor.name not in unvisited:
                    continue
                cost = self.ZONE_COST[neighbor.zone_type]
                new_dist = distances_from_start[current_name] + cost

                if new_dist < distances_from_start[neighbor.name]:
                    distances_from_start[neighbor.name] = new_dist
                    previous_hub[neighbor.name] = current_name
        return None

    def find_closest_unvisited(
        self, distances: dict[str, float], unvisited: set[str]
    ) -> str | None:
        if not unvisited:
            return None
        return min(unvisited, key=lambda name: distances[name])

    def recreate_path(
        self, previous: dict[str, str], start_name: str, end_name: str
    ) -> list[Hub]:
        path_names = [end_name]
        current = end_name
        while current != start_name:
            current = previous[current]
            path_names.append(current)
        path_names.reverse()
        return [self.graph.get_hub(name) for name in path_names]
