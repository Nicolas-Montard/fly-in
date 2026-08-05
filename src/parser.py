from typing import Any
from . import Graph, Hub, Connection, Drone


class ParsingError(Exception):
    """Raised when the map file contains invalid or malformed data.

    Carries the offending line number (when known) so the caller can
    report a precise, actionable error message to the user.

    Attributes:
        message: Description of what went wrong.
        line: Line number in the map file where the error occurred,
            or None if the error isn't tied to a specific line.
    """
    def __init__(self, message: str, line: int | None = None):
        self.ligne = line
        self.message = message
        if line is not None:
            full_message = f"Error at line {line} of the map: {message}"
        else:
            full_message = f"Error in the map: {message}"
        super().__init__(full_message)


class Parser:
    """Parses a map file into validated data, then builds a Graph from it.

    Reads the map file line by line, validating syntax and semantics
    as it goes (unique names, valid coordinates, valid metadata,
    known zone types, no duplicate connections, etc.), then assembles
    the parsed data into a ready-to-use Graph via `build_graph`.

    Attributes:
        map_path: Path to the map file to parse.
        counter_line: Current line number being processed, used for
            error reporting.
        data: Parsed top-level data (nb_drones, start_hub, end_hub,
            hubs, connections).
        hubs: Parsed regular (non start/end) hub definitions, as raw dicts.
        connections: Parsed connection definitions, as raw dicts.
        hub_names: Set of hub names already seen, used to detect duplicates.
        hub_coord: Set of hub coordinates already seen, used to detect
            duplicates.
        connection_seen: Set of normalized (sorted) hub name pairs
            already connected, used to detect duplicate connections.
    """
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
        """Read and validate the entire map file, line by line.

        Skips blank lines and comments, dispatches each meaningful
        line to the appropriate validation method based on its key
        (nb_drones, start_hub, end_hub, hub, connection), and
        populates `self.data`, `self.hubs`, and `self.connections`
        as it goes.

        Raises:
            ParsingError: If any line is malformed, uses an unknown
                key, or otherwise violates the map format.
        """
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
        """Validate the map's first line and extract the drone count.

        Args:
            line: The first non-comment, non-blank line of the map file.

        Raises:
            ParsingError: If the line isn't a valid `nb_drones: <int>`
                declaration, or the value isn't a non-negative integer.
        """
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
        """Validate a hub definition line and store the parsed hub.

        Handles `start_hub:`, `end_hub:`, and `hub:` lines alike,
        parsing the name, coordinates, and optional metadata. Regular
        hubs are appended to `self.hubs`; start_hub/end_hub are stored
        directly in `self.data`.

        Args:
            line: A `start_hub:`, `end_hub:`, or `hub:` line from the
                map file.

        Raises:
            ParsingError: If start_hub/end_hub is defined more than
                once, the value count is wrong, the name/coordinates
                are invalid, or the metadata is invalid.
        """
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
        """Parse a `[key=value key2=value2 ...]` metadata block into a dict.

        Args:
            metadata: The raw metadata block, including its surrounding
                brackets.

        Returns:
            A dict mapping each metadata key to its raw string value.

        Raises:
            ParsingError: If the block doesn't start with `[` and end
                with `]`.
        """
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
        """Validate a hub name and register it as seen.

        Args:
            name: The hub name to validate.

        Raises:
            ParsingError: If the name contains a dash, or a hub with
                this name has already been defined.
        """
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
        """Validate a hub's coordinates and register them as seen.

        Args:
            x_str: The hub's x coordinate, as a raw string.
            y_str: The hub's y coordinate, as a raw string.

        Raises:
            ParsingError: If the coordinates aren't valid integers, or
                these exact coordinates are already used by another hub.
        """
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
        """Validate a hub's metadata in place and normalize its keys.

        Checks that only known keys are present, that `zone` (if any)
        is a valid zone type, and that `max_drones` (if any) is a
        non-negative integer. Converts `max_drones` to an int, and
        renames the `zone` key to `zone_type` to match the Hub model.

        Args:
            metadata: The raw metadata dict to validate, modified in place.

        Raises:
            ParsingError: If an unknown key is present, `zone` isn't a
                valid zone type, or `max_drones` isn't a valid
                non-negative integer.
        """
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
                if metadata[key] < 0:
                    raise ParsingError(
                        f"The metadata {key} cannot be inferior to 0",
                        self.counter_line
                    )
        if "zone" in metadata:
            metadata["zone_type"] = metadata.pop("zone")

    def split_line(self, line: str) -> list[str]:
        """Split a line into its key and value, on the first ':'.

        Args:
            line: The raw line to split.

        Returns:
            A two-element list: [key, value], with the value stripped
            of leading/trailing spaces.

        Raises:
            ParsingError: If the line doesn't contain a ':' separator.
        """
        split_line = line.split(":", 1)
        if len(split_line) <= 1:
            raise ParsingError(
                "value isn't separated by ':'",
                self.counter_line,
            )
        split_line[1] = split_line[1].strip(" ")
        return split_line

    def verif_connection(self, line: str) -> None:
        """Validate a connection line and store the parsed connection.

        Parses the `hub1-hub2` name pair, checks both hubs are already
        defined, rejects duplicate connections (regardless of hub
        order), and parses any optional metadata.

        Args:
            line: A `connection:` line from the map file.

        Raises:
            ParsingError: If the hub pair isn't formatted as exactly
                one dash-separated pair, either hub name is unknown,
                the connection is already defined, or the metadata is
                invalid.
        """
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
        """Validate a connection's metadata in place.

        Checks that only `max_link_capacity` is present, and that its
        value is a non-negative integer (converting it from string to
        int in the process).

        Args:
            metadata: The raw metadata dict to validate, modified in place.

        Raises:
            ParsingError: If an unknown key is present, or
                `max_link_capacity` isn't a valid non-negative integer.
        """
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
                if metadata[key] < 0:
                    raise ParsingError(
                        f"The metadata {key} cannot be inferior to 0",
                        self.counter_line
                    )

    def build_graph(self) -> Graph:
        """Build a ready-to-use Graph from the previously parsed data.

        Must be called after `read_data`. Constructs the start and end
        hubs, all regular hubs, all connections, and one drone per
        `nb_drones`, all starting at the start hub.

        Returns:
            The fully assembled Graph.

        Raises:
            ParsingError: If no start_hub or no end_hub was defined.
        """
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
