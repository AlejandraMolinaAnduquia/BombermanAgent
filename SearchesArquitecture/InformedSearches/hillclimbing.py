from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.metal import MetalAgent
from AgentArquitecture.globe import GlobeAgent

class HillClimbing(SearchStrategy):
    def __init__(self):
        self.step_count = 0
        self.visited_nodes = set()  # Conjunto para almacenar los nodos visitados
        self.path_to_goal = []  # Almacena el camino hacia la meta
        self.current = None  # Nodo actual
        self.goal = None  # Nodo objetivo

    def start_search(self, start, goal):
        """Inicia la búsqueda Hill Climbing desde el nodo de inicio."""
        self.goal = goal
        self.current = start  # Comienza desde el nodo inicial
        self.step_count = 0  # Resetea el contador de pasos de expansión
        self.visited_nodes.clear()  # Limpia los nodos visitados al iniciar la búsqueda
        self.path_to_goal.clear()  # Resetea el camino a la meta

    def heuristic(self, position):
        """Define la heurística: distancia de Manhattan al objetivo."""
        return abs(position[0] - self.goal[0]) + abs(position[1] - self.goal[1])

    def explore_step(self, agent):
        """Expande el siguiente nodo en el algoritmo de Hill Climbing con backtracking."""
        self.step_count += 1
        print(f"Paso {self.step_count}: Evaluando nodo {self.current}")

        # Verifica que el nodo actual no sea None y esté dentro de los límites
        if self.current is None or not (0 <= self.current[0] < agent.model.grid.width) or not (0 <= self.current[1] < agent.model.grid.height):
            print("Nodo actual no válido:", self.current)
            return None

        # Marca la celda con el nivel actual si no ha sido visitada
        if self.current not in self.visited_nodes:
            cell = agent.model.grid[self.current[0]][self.current[1]]
            if cell is not None:
                cell[0].visit_order = self.step_count
                self.visited_nodes.add(self.current)
                self.path_to_goal.append(self.current)

        # Verifica si el nodo actual es la meta
        agents_in_cell = agent.model.grid[self.current[0]][self.current[1]]
        if any(isinstance(a, GoalAgent) for a in agents_in_cell):
            agent.path_to_exit = self.path_to_goal
            agent.has_explored = True
            print("Meta alcanzada en:", self.current)
            return None

        # Si no se ha alcanzado la meta, continúa explorando
        neighbors = self.get_neighbors(agent, self.current)
        
        # Filtra vecinos válidos permitiendo RockAgent y GlobeAgent pero no MetalAgent
        valid_neighbors = []
        for neighbor in neighbors:
            agents_at_neighbor = agent.model.grid[neighbor[0]][neighbor[1]]
            if neighbor not in self.visited_nodes:
                if any(isinstance(a, MetalAgent) for a in agents_at_neighbor):
                    continue  # No considera nodos con MetalAgent
                else:
                    # Permite nodos con RockAgent o GlobeAgent
                    valid_neighbors.append(neighbor)

        if valid_neighbors:
            # Selecciona el vecino con la mejor heurística entre los válidos
            next_node = min(valid_neighbors, key=lambda neighbor: self.heuristic(neighbor))
            self.current = next_node
            print(f"Moviendo a {self.current} basado en la heurística")
        else:
            # No hay vecinos válidos, inicia retroceso
            print("No hay vecinos válidos, iniciando retroceso...")
            if self.path_to_goal:
                # Deshace el último movimiento en el camino hacia la meta
                self.path_to_goal.pop()  # Elimina el último nodo del camino actual
                if self.path_to_goal:
                    # Si aún quedan nodos en el camino, vuelve al anterior
                    self.current = self.path_to_goal[-1]
                    print(f"Retrocediendo a {self.current}")
                else:
                    # Si no quedan nodos, ha vuelto al inicio y no hay rutas posibles
                    print("No hay más nodos por retroceder. Fin de la búsqueda.")
                    self.current = None
            else:
                print("Retroceso imposible, ningún camino alternativo disponible.")
                self.current = None

        return None

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