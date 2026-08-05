from . import Parser, Simulation


class Launcher:
    """Entry point that wires together parsing, graph building, and simulation.

    Prompts the user for a map file, parses it into a graph, and runs
    the drone simulation on it. Any error raised during this process
    (parsing errors, missing start/end hub, unreachable goal, etc.) is
    caught and printed rather than crashing the program.
    """
    @staticmethod
    def launch() -> None:
        """Run the full pipeline: prompt for a map, parse it, and simulate it.

        Catches and prints any exception raised while parsing the map
        or running the simulation, so the program exits cleanly instead
        of crashing on invalid input.
        """
        try:
            map_name = Launcher.get_mapname()
            parser = Parser(map_name)
            parser.read_data()
            graph = parser.build_graph()
            simulation = Simulation(graph)
            simulation.run()
        except Exception as error:
            print(error)

    @staticmethod
    def get_mapname() -> str:
        """Prompt the user for a map file path and return it."""
        value = input("Map name (including path):")
        return value
