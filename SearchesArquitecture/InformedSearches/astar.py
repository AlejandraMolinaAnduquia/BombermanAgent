from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
import heapq

class AStarSearch(SearchStrategy):
    def __init__(self):
        self.open_set = []  # Cola de prioridad
        self.visited = set()
        self.g_score = {}  # Costo acumulado
        self.step_count = 0
        self.index = 0

    def manhattan_distance(self, pos1, pos2):
        """Calcula la distancia de Manhattan entre dos posiciones."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def start_search(self, start, goal):
        """Inicia la búsqueda A* desde el nodo de inicio."""
        self.goal = goal
        self.open_set = []  # Reinicia la cola de prioridad para cada búsqueda
        start_tuple = (start, [])
        heapq.heappush(self.open_set, (0, self.index, start_tuple[0], [start_tuple[0]]))
        self.g_score[start_tuple[0]] = 0
        self.index += 1
        self.step_count = 0  # Resetea el contador de pasos de expansión

    def explore_step(self, agent, diagonal=False):
        """Expande el siguiente nodo en la cola de prioridad."""
        if not self.open_set:
            return None

        # Extrae el nodo con menor f_score
        _, _, current, path = heapq.heappop(self.open_set)

        # Imprime el orden de expansión de cada nodo
        self.step_count += 1
        print(f"Expandiendo nodo {self.step_count}: {current}, Camino acumulado hasta ahora: {path}")

        # Marca la celda en el orden de expansión
        agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count

        # Verifica si el nodo actual es la meta
        agents_in_cell = agent.model.grid[current[0]][current[1]]
        if any(isinstance(a, GoalAgent) for a in agents_in_cell):
            agent.path_to_exit = path
            agent.has_explored = True
            print("Meta alcanzada. Camino óptimo calculado:", path)
            return None

        # Agrega a visitados
        self.visited.add(current)

        # Direcciones ortogonales (sin diagonales)
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

                # Permite rocas y caminos, ignora solo el metal
                if all(isinstance(agent, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for agent in agents_in_new_cell):
                    tentative_g_score = self.g_score[current] + 10  # Costo de movimiento

                    # Calcula la heurística (distancia de Manhattan)
                    h_score = self.manhattan_distance(new_position, self.goal)
                    f_score = tentative_g_score + h_score

                    # Solo agregar si es una mejor ruta al nodo
                    if new_position not in self.g_score or tentative_g_score < self.g_score[new_position]:
                        self.g_score[new_position] = tentative_g_score
                        heapq.heappush(self.open_set, (f_score, self.index, new_position, path + [new_position]))
                        self.index += 1

        return current

