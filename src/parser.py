from typing import Any
from . import Graph, Hub, Connection, Drone


class ParsingError(Exception):
    def __init__(self, message: str, ligne: int | None = None):
        self.ligne = ligne
        self.message = message
        if ligne is not None:
            full_message = f"Error at line {ligne} of the map: {message}"
        else:
            full_message = f"Error in the map: {message}"
        super().__init__(full_message)


class Parser:
    def __init__(self, map_path: str) -> None:
        self.map_path: str = map_path
        self.counter_line: int = 0
        self.data: dict[str, Any] = {}
        self.hubs: list[dict[str, Any]] = []
        self.connections: list[dict[str, Any]] = []
        self.data["hubs"] = self.hubs
        self.data["connections"] = self.connections
        self.hub_names: set[str] = set()
        self.hub_coord: set[tuple[int, int]] = set()
        self.connection_seen: set[tuple[str, str]] = set()

    def read_data(self) -> None:
        with open(self.map_path, "r") as file:
            start_line = next(file).lstrip(" ").rstrip("\r\n")
            self.counter_line += 1
            while not start_line or start_line[0] == "#":
                start_line = next(file).lstrip(" ").rstrip("\r\n")
                self.counter_line += 1
            self.verif_nb_drone_line(start_line)
            for line in file:
                self.counter_line += 1
                line = line.rstrip("\r\n").lstrip(" ")
                if not line:
                    continue
                if line[0] == "#":
                    continue
                line_type = line.split(":")[0]
                if line_type in ("start_hub", "end_hub", "hub"):
                    self.verif_hub_line(line)
                    continue
                if line_type == "connection":
                    self.verif_connection(line)
                    continue
                raise ParsingError(f"{line_type} is not a valid key",
                                   self.counter_line)

    def verif_nb_drone_line(self, line: str) -> None:
        split_line = self.split_line(line)
        if split_line[0] != "nb_drones":
            raise ParsingError(
                "The first line isn't nb_drones: "
                f"{split_line[0]}", self.counter_line
            )
        try:
            nb_drones = int(split_line[1])
            if nb_drones < 0:
                raise ValueError
        except ValueError:
            raise ParsingError(
                "The Value of nb_drone is invalid: " f"{split_line[1]}",
                self.counter_line,
            )
        self.data["nb_drones"] = nb_drones

    def verif_hub_line(self, line: str) -> None:
        split_line = self.split_line(line)
        if split_line[0] == "start_hub":
            if "start_hub" in self.data:
                raise ParsingError("start_hub is already defined",
                                   self.counter_line)
        if split_line[0] == "end_hub":
            if "end_hub" in self.data:
                raise ParsingError("end_hub is already defined",
                                   self.counter_line)
        values = split_line[1].split(" ", 3)
        if len(values) != 4 and len(values) != 3:
            raise ParsingError(
                f"{len(values)} values found, 3 or 4 expected",
                self.counter_line
            )
        self.verif_hub_name(values[0])
        self.verif_hub_coord(values[1], values[2])
        hub = {"name": values[0], "x": int(values[1]), "y": int(values[2])}
        if len(values) == 4:
            formated_metadata = self.format_metadata(values[3])
            if split_line[0] in ("start_hub", "end_hub"):
                formated_metadata.pop("max_drones", None)
            self.verif_hub_metadata(formated_metadata)
            hub.update(formated_metadata)
        if split_line[0] == "hub":
            self.hubs.append(hub)
        else:
            self.data[split_line[0]] = hub

    def format_metadata(self, metadata: str) -> dict:
        if metadata[0] != "[" or metadata[-1] != "]":
            raise ParsingError(
                "The metadata must begin and end with [], "
                f"actual: {metadata}",
                self.counter_line
            )
        metadata = metadata.lstrip("[").rstrip("]")
        split_metadata = metadata.split(" ")
        dict_metadata = {}
        for data in split_metadata:
            key, value = data.split("=", 1)
            dict_metadata[key] = value
        return dict_metadata

    def verif_hub_name(self, name: str) -> None:
        if "-" in name:
            raise ParsingError(
                f"The name of the hub contain a dashes: {name}",
                self.counter_line
            )
        if name in self.hub_names:
            raise ParsingError(
                f"This hub name is already defined: {name}",
                self.counter_line
            )
        self.hub_names.add(name)

    def verif_hub_coord(self, x_str: str, y_str: str) -> None:
        try:
            x, y = int(x_str), int(y_str)
        except ValueError:
            raise ParsingError(f"Invalid coordonate: {x_str, y_str}",
                               self.counter_line)
        if (x, y) in self.hub_coord:
            raise ParsingError(
                f"Those coordinate are already defined: {x, y}",
                self.counter_line
            )
        self.hub_coord.add((x, y))

    def verif_hub_metadata(self, metadata: dict) -> None:
        zone_type = ("normal", "blocked", "restricted", "priority")
        for key, value in metadata.items():
            if key not in ("zone", "color", "max_drones"):
                raise ParsingError(
                    f"The metadata {key} is not a valid type, "
                    "valid type are: zone, color, max_drones",
                    self.counter_line,
                )
            if key == "zone":
                if value not in zone_type:
                    raise ParsingError(
                        f"The metadata {key} cannot have this value",
                        self.counter_line
                    )
            if key == "max_drones":
                try:
                    metadata[key] = int(value)
                except ValueError:
                    raise ParsingError(
                        f"The metadata {key} is not a valid integer",
                        self.counter_line
                    )
                if metadata[key] < 1:
                    raise ParsingError(
                        f"The metadata {key} cannot be inferior to 1",
                        self.counter_line
                    )
        if "zone" in metadata:
            metadata["zone_type"] = metadata.pop("zone")

    def split_line(self, line: str) -> list[str]:
        split_line = line.split(":", 1)
        if len(split_line) <= 1:
            raise ParsingError(
                "value isn't separated by ':'",
                self.counter_line,
            )
        split_line[1] = split_line[1].strip(" ")
        return split_line

    def verif_connection(self, line: str) -> None:
        split_line = self.split_line(line)
        values = split_line[1].split(" ")
        if values[0].count("-") != 1:
            raise ParsingError(f"{values[0]} must have one '-'",
                               self.counter_line)
        hub1, hub2 = values[0].split("-")
        if hub1 not in self.hub_names or hub2 not in self.hub_names:
            raise ParsingError(
                f"{values[0]} contain at least 1 invalid" "hub name",
                self.counter_line
            )
        h1, h2 = tuple(sorted((hub1, hub2)))
        unique_connection = (h1, h2)
        if unique_connection in self.connection_seen:
            raise ParsingError(
                f"connection {values[0]} already defined", self.counter_line
            )
        self.connection_seen.add(unique_connection)
        connection = {"hub_name1": hub1, "hub_name2": hub2}
        if len(values) > 1:
            metadata = self.format_metadata(values[1])
            self.verif_connection_metadata(metadata)
            connection.update(metadata)
        self.connections.append(connection)

    def verif_connection_metadata(self, metadata: dict) -> None:
        for key, value in metadata.items():
            if key not in ("max_link_capacity",):
                raise ParsingError(
                    f"The metadata {key} "
                    "is not a valid type, "
                    "valid type are: max_link_capacity",
                    self.counter_line,
                )
            if key == "max_link_capacity":
                try:
                    metadata[key] = int(value)
                except ValueError:
                    raise ParsingError(
                        f"The metadata {key} is not a valid integer",
                        self.counter_line
                    )
                if metadata[key] < 1:
                    raise ParsingError(
                        f"The metadata {key} cannot be inferior to 1",
                        self.counter_line
                    )

    def build_graph(self) -> Graph:
        if "start_hub" not in self.data:
            raise ParsingError("no start_hub defined")
        if "end_hub" not in self.data:
            raise ParsingError("no end_hub defined")
        graph = Graph()
        start_hub = Hub(**self.data["start_hub"])
        end_hub = Hub(**self.data["end_hub"])
        graph.add_hub(start_hub)
        graph.add_hub(end_hub)
        graph.start = start_hub
        graph.end = end_hub

        for hub_data in self.hubs:
            graph.add_hub(Hub(**hub_data))

        for conn_data in self.connections:
            hub1 = graph.get_hub(conn_data["hub_name1"])
            hub2 = graph.get_hub(conn_data["hub_name2"])
            connection = Connection(
                hub1=hub1,
                hub2=hub2,
                max_link_capacity=conn_data.get("max_link_capacity", 1),
            )
            graph.add_connection(connection)
        drones = [
            Drone(id=i + 1, location=start_hub) for i in
            range(self.data["nb_drones"])
        ]
        for drone in drones:
            graph.drones.append(drone)

        return graph
