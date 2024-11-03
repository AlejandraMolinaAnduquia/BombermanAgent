from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent

class BeamSearch(SearchStrategy):
    def __init__(self, beta):
        super().__init__()
        self.beta = beta  # Número máximo de nodos hijos a considerar en cada nivel

    def start_search(self, start, goal):
        """Inicia la búsqueda Beam desde el nodo de inicio."""
        self.goal = goal
        self.visited = set()
        self.queue = []  # Cola para almacenar nodos a explorar
        self.queue.append((start, [start]))  # Inicializa con el nodo de inicio

    def explore_step(self, agent):
        """Expande el siguiente nivel en la búsqueda Beam."""
        if not self.queue:
            print("No hay más nodos para explorar.")
            return None

        # Lista para almacenar nodos hijos en el nivel actual
        next_level = []

        # Expande todos los nodos en la cola actual
        for current, path in self.queue:
            # Marca el nodo actual como visitado
            self.visited.add(current)

            # Verifica si el nodo actual es la meta
            agents_in_cell = agent.model.grid[current[0]][current[1]]
            if any(isinstance(a, GoalAgent) for a in agents_in_cell):
                agent.path_to_exit = path
                agent.has_explored = True
                print("Meta alcanzada. Camino óptimo calculado:", path)
                return None

            # Direcciones ortogonales
            directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

            # Expande cada dirección
            for direction in directions:
                new_x, new_y = current[0] + direction[0], current[1] + direction[1]
                new_position = (new_x, new_y)

                # Verifica límites y si es metal (bloqueo)
                if (
                    0 <= new_x < agent.model.grid.width
                    and 0 <= new_y < agent.model.grid.height
                    and new_position not in self.visited
                ):
                    agents_in_new_cell = agent.model.grid[new_x][new_y]
                    if all(isinstance(agent, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for agent in agents_in_new_cell):
                        next_level.append((new_position, path + [new_position]))

        # Seleccionar los mejores nodos para el siguiente nivel según el valor de beta
        next_level.sort(key=lambda x: self.manhattan_distance(x[0], self.goal))  # Ordenar por distancia
        self.queue = next_level[:self.beta]  # Tomar solo los primeros 'beta' nodos

        # Retornar el primer nodo explorado en este paso
        return current

    def manhattan_distance(self, pos1, pos2):
        """Calcula la distancia de Manhattan entre dos posiciones."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
