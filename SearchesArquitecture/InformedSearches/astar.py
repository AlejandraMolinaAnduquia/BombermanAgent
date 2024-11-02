from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
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

    def explore_step(self, agent, diagonal=False):
        """Expande el siguiente nodo en la cola de prioridad."""
        if not self.open_set:
            return None

        # Extrae el nodo con menor f_score
        _, _, current, path = heapq.heappop(self.open_set)

        # Marca la celda en el orden de expansión
        agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count
        self.step_count += 1

        # Verifica si el nodo actual es la meta
        AgentArquitecture_in_cell = agent.model.grid[current[0]][current[1]]
        if any(isinstance(a, GoalAgent) for a in AgentArquitecture_in_cell):
            agent.path_to_exit = path
            agent.has_explored = True
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
                AgentArquitecture_in_new_cell = agent.model.grid[new_x][new_y]

                # Permite rocas y caminos, ignora solo el metal
                if all(isinstance(agent, (RoadAgent, GoalAgent, RockAgent)) for agent in AgentArquitecture_in_new_cell):
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


    def get_path(self, start, goal, model):
        """Calcula el camino óptimo de `start` a `goal` usando A* y devuelve una lista de posiciones."""
        from AgentArquitecture.bomb import BombAgent
        from AgentArquitecture.metal import MetalAgent
        self.open_set = []  # Reinicia la cola de prioridad para cada búsqueda
        self.visited = set()
        self.g_score = {start: 0}
        heapq.heappush(self.open_set, (0, self.index, start, [start]))
        self.index += 1

        while self.open_set:
            _, _, current, path = heapq.heappop(self.open_set)

            # Si hemos alcanzado la meta, devolvemos el camino
            if current == goal:
                return path

            self.visited.add(current)

            # Explora las celdas adyacentes
            directions = [(-1, 0), (1, 0), (0, -1)]
            for direction in directions:
                neighbor = (current[0] + direction[0], current[1] + direction[1])

                # Verifica que la posición esté dentro de los límites y no sea un obstáculo
                if model.grid.out_of_bounds(neighbor) or neighbor in self.visited:
                    continue

                agents_in_neighbor = model.grid.get_cell_list_contents([neighbor])
                if any(isinstance(agent, (RockAgent, MetalAgent, BombAgent)) for agent in agents_in_neighbor):
                    continue  # Ignora celdas que no son transitables

                # Calcula el costo hasta el vecino y evalúa la heurística
                tentative_g_score = self.g_score[current] + 1  # Cada movimiento tiene un costo de 1
                if neighbor not in self.g_score or tentative_g_score < self.g_score[neighbor]:
                    self.g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + self.manhattan_distance(neighbor, goal)
                    heapq.heappush(self.open_set, (f_score, self.index, neighbor, path + [neighbor]))
                    self.index += 1

        # Si no se encuentra un camino, devuelve una lista vacía
        return []
