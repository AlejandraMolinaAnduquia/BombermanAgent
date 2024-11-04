from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent

class HillClimbing(SearchStrategy):
    def __init__(self):
        self.step_count = 0
        self.visited_nodes = set()  # Conjunto para almacenar los nodos visitados
        self.path_to_goal = []  # Almacena el camino hacia la meta
        self.backtrack_stack = []  # Pila para niveles con nodos pendientes de visitar
        self.current_level = 0  # Nivel actual de profundidad

    def start_search(self, start, goal):
        """Inicia la búsqueda Hill Climbing desde el nodo de inicio."""
        self.goal = goal
        self.current = start  # Comienza desde el nodo inicial
        self.step_count = 0  # Resetea el contador de pasos de expansión
        self.visited_nodes.clear()  # Limpia los nodos visitados al iniciar la búsqueda
        self.path_to_goal.clear()  # Resetea el camino a la meta
        self.backtrack_stack.clear()  # Resetea la pila de backtracking
        self.current_level = 0

    def heuristic(self, position):
        """Define la heurística: distancia de Manhattan al objetivo."""
        return abs(position[0] - self.goal[0]) + abs(position[1] - self.goal[1])

    def explore_step(self, agent):
        """Expande el siguiente nodo en el algoritmo de Hill Climbing."""
        self.step_count += 1
        print(f"Paso {self.step_count}: Evaluando nodo {self.current} en nivel {self.current_level}")

        # Marca la celda con el nivel actual si no ha sido visitada
        if self.current not in self.visited_nodes:
            agent.model.grid[self.current[0]][self.current[1]][0].visit_order = self.step_count
            self.visited_nodes.add(self.current)  # Agrega el nodo al conjunto de visitados
            self.path_to_goal.append(self.current)  # Agrega el nodo actual al camino

        # Verifica si el nodo actual es la meta
        agents_in_cell = agent.model.grid[self.current[0]][self.current[1]]
        if any(isinstance(a, GoalAgent) for a in agents_in_cell):
            agent.path_to_exit = self.path_to_goal  # Asigna el camino encontrado hasta la meta
            agent.has_explored = True
            print("Meta alcanzada en:", self.current)
            return None

        # Genera los vecinos del nodo actual
        neighbors = self.get_neighbors(agent, self.current)

        # Encuentra el vecino con la menor heurística
        next_node = None
        min_heuristic_value = float('inf')
        level_has_unvisited_neighbors = False

        for neighbor in neighbors:
            if neighbor not in self.visited_nodes:  # Ignora vecinos ya visitados
                h_value = self.heuristic(neighbor)
                if h_value < min_heuristic_value:
                    min_heuristic_value = h_value
                    next_node = neighbor
                    level_has_unvisited_neighbors = True

        # Si no hay un mejor vecino, se ha llegado a un óptimo local
        if not level_has_unvisited_neighbors:
            print("Se ha llegado a un óptimo local en:", self.current)
            # Si estamos en un nivel sin vecinos no visitados, retrocede al último nivel con nodos sin visitar
            if self.backtrack_stack:
                last_level_with_nodes = self.backtrack_stack.pop()
                self.current, self.current_level = last_level_with_nodes
                print(f"Retrocediendo a nivel {self.current_level} en nodo {self.current}")
                return self.current
            else:
                # Si no hay más niveles en la pila, termina la búsqueda
                agent.path_to_exit = self.path_to_goal  # Devuelve el camino recorrido hasta el óptimo local
                return None

        # Si hay vecinos, guarda el nivel actual en la pila si no está completamente explorado
        if self.current_level == len(self.backtrack_stack):
            self.backtrack_stack.append((self.current, self.current_level))

        # Actualiza el nodo actual y el nivel
        self.current = next_node
        self.current_level += 1
        return self.current

    def get_neighbors(self, agent, current):
        """Obtiene los vecinos válidos del nodo actual."""
        neighbors = []
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Direcciones ortogonales

        for direction in directions:
            new_x, new_y = current[0] + direction[0], current[1] + direction[1]
            new_position = (new_x, new_y)

            # Verifica límites y validez del vecino
            if (
                0 <= new_x < agent.model.grid.width
                and 0 <= new_y < agent.model.grid.height
            ):
                agents_in_new_cell = agent.model.grid[new_x][new_y]
                if all(isinstance(agent, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for agent in agents_in_new_cell):
                    neighbors.append(new_position)

        return neighbors
