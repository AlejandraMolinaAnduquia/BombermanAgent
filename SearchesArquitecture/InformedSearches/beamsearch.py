from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
import math

class BeamSearch(SearchStrategy):
    def __init__(self, beam_width=3, heuristic='Manhattan'):
        self.beam_width = beam_width  # Limita el número de caminos a explorar en cada paso
        self.open_set = []  # Lista de caminos en el haz actual
        self.visited = set()  # Nodos ya explorados
        self.step_count = 0  # Contador de pasos
        self.heuristic = heuristic  # Heurística de elección (Manhattan o Euclidean)

    def start_search(self, start, goal):
        self.goal = goal
        self.open_set = [[start]]
        self.visited = set()
        self.step_count = 0

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def euclidean_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def explore_step(self, agent):
        if not self.open_set:
            return None

        # Extrae todos los caminos actuales en el open_set
        new_paths = []
        for path in self.open_set:
            current = path[-1]
            if current not in self.visited:
                self.visited.add(current)
                self.step_count += 1
                agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count
                print(f"Expandiendo camino {self.step_count}: {path}, Última posición: {current}")

                agents_in_cell = agent.model.grid[current[0]][current[1]]
                if any(isinstance(a, GoalAgent) for a in agents_in_cell):
                    agent.path_to_exit = path
                    agent.has_explored = True
                    print("Meta alcanzada. Camino óptimo calculado:", path)
                    return None

                # Obtén los vecinos y genera nuevos caminos para cada vecino
                neighbors = self.get_neighbors(agent, current)
                for neighbor in neighbors:
                    if neighbor not in self.visited:
                        new_paths.append(path + [neighbor])

        # Ordena los nuevos caminos según su heurística (Manhattan o Euclidean)
        self.open_set = sorted(new_paths, key=lambda p: self.evaluate_path(p))[:self.beam_width]
        
        return self.open_set[0] if self.open_set else None

    def get_neighbors(self, agent, current):
        """
        Obtiene los vecinos válidos del nodo actual con prioridad: Izquierda, Arriba, Derecha, Abajo.
        """
        neighbors = []
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Prioridad: Izquierda, Arriba, Derecha, Abajo
        for direction in directions:
            new_x, new_y = current[0] + direction[0], current[1] + direction[1]
            new_position = (new_x, new_y)
            if (
                0 <= new_x < agent.model.grid.width
                and 0 <= new_y < agent.model.grid.height
            ):
                agents_in_new_cell = agent.model.grid[new_x][new_y]
                if all(isinstance(agent, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for agent in agents_in_new_cell):
                    neighbors.append(new_position)
        return neighbors

    def evaluate_path(self, path):
        """
        Evalúa el camino basándose en la distancia Manhattan o Euclídea, según la heurística seleccionada.
        """
        if self.heuristic == 'Manhattan':
            return self.manhattan_distance(path[-1], self.goal)
        elif self.heuristic == 'Euclidean':
            return self.euclidean_distance(path[-1], self.goal)
        else:
            raise ValueError("Heurística no válida. Use 'Manhattan' o 'Euclidean'.")
