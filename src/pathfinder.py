from . import Graph, Hub


class Pathfinder:
    """Computes the shortest path from a graph's start hub to its end hub.

    Uses Dijkstra's algorithm, where the cost of entering a hub
    depends on its zone type (see ZONE_COST). Blocked zones, full
    hubs, and full connections are treated as impassable.

    Attributes:
        graph: The graph to search.
    """

    ZONE_COST = {
        "normal": 1,
        "priority": 0.99,
        "restricted": 2,
    }
    """Movement cost of entering a hub, per zone type. Blocked zones
    have no entry since they're skipped before this lookup."""

    def __init__(self, graph: Graph) -> None:
        self.graph: Graph = graph

    def find_shortest_path(self) -> list[Hub] | None:
        """Find the lowest-cost path from the graph's start to its end.

        Runs Dijkstra's algorithm over the graph, skipping blocked
        zones and any hub or connection that cannot be reached.

        Returns:
            The path as an ordered list of Hub instances, from start
            to end (inclusive), or None if the end is unreachable.
        """
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
                if neighbor.get_max_capacity() < 1:
                    continue
                if connection.get_max_capacity() < 1:
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
        """Return the unvisited hub name with the smallest known distance.

        Args:
            distances: Current shortest known distance to each hub.
            unvisited: Names of hubs not yet finalized by the algorithm.

        Returns:
            The closest unvisited hub's name, or None if `unvisited` is empty.
        """
        if not unvisited:
            return None
        return min(unvisited, key=lambda name: distances[name])

    def recreate_path(
        self, previous: dict[str, str], start_name: str, end_name: str
    ) -> list[Hub]:
        """Rebuild the path from start to end using backtracking pointers.

        Args:
            previous: Maps each hub name to the name of the hub it was
                reached from during the search.
            start_name: Name of the path's starting hub.
            end_name: Name of the path's ending hub.

        Returns:
            The path as an ordered list of Hub instances, from
            `start_name` to `end_name` (inclusive).
        """
        path_names = [end_name]
        current = end_name
        while current != start_name:
            current = previous[current]
            path_names.append(current)
        path_names.reverse()
        return [self.graph.get_hub(name) for name in path_names]
