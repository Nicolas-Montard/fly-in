from . import Parser, Simulation


class Launcher:
    @staticmethod
    def launch() -> None:
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
        value = input("Map name (including path):")
        return value
