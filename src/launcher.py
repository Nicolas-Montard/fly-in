from . import Parser, Simulation

class Launcher():
    @staticmethod
    def launch():
        try:
            parser = Parser("maps/easy/01_linear_path.txt")
            parser.read_data()
            graph = parser.build_graph()
            simulation = Simulation(graph)
            simulation.run()
        except Exception as error:
            print(error)