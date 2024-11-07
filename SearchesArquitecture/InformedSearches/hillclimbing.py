from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.metal import MetalAgent
from AgentArquitecture.globe import GlobeAgent
import math

class HillClimbing(SearchStrategy):
    """
    Implementa el algoritmo de Hill Climbing con retroceso. Este enfoque selecciona en cada paso el vecino
    que maximiza la heurística (distancia de Manhattan o Euclidiana al objetivo), y retrocede si no encuentra una mejor opción.
    
    Atributos:
        step_count (int): Número de pasos de expansión, usado para visualizar el progreso.
        visited_nodes (set): Conjunto de nodos ya visitados.
        path_to_goal (list): Lista de nodos en el camino explorado hasta el momento.
        current (tuple): Nodo actual en el proceso de exploración.
        goal (tuple): Nodo objetivo de la búsqueda.
        heuristic (str): Tipo de heurística seleccionada, puede ser 'Manhattan' o 'Euclidean'.
    """

    def __init__(self, heuristic='Manhattan'):
        """
        Inicializa los atributos necesarios para la búsqueda Hill Climbing.
        
        Args:
            heuristic (str): Tipo de heurística, puede ser 'Manhattan' o 'Euclidean'.
        """
        self.step_count = 0
        self.visited_nodes = set()
        self.path_to_goal = []
        self.current = None
        self.goal = None
        self.heuristic = heuristic
        self.retrogress_count = 0
        self.optimal_path = []

    def start_search(self, start, goal):
        """
        Inicia la búsqueda Hill Climbing desde el nodo de inicio hacia el objetivo.
        
        Args:
            start (tuple): Coordenadas del nodo de inicio.
            goal (tuple): Coordenadas del nodo objetivo.
        """
        self.goal = goal
        self.current = start
        self.step_count = 0
        self.visited_nodes.clear()
        self.path_to_goal.clear()
        self.optimal_path.clear()

    def manhattan_distance(self, position):
        """Calcula la distancia de Manhattan entre la posición actual y la meta."""
        return abs(position[0] - self.goal[0]) + abs(position[1] - self.goal[1])

    def euclidean_distance(self, position):
        """Calcula la distancia Euclidiana entre la posición actual y la meta."""
        return math.sqrt((position[0] - self.goal[0]) ** 2 + (position[1] - self.goal[1]) ** 2)

    def heuristica(self, position):
        """Calcula la heurística para un nodo dado."""
        return self.manhattan_distance(position) if self.heuristic == 'Manhattan' else self.euclidean_distance(position)

    def explore_step(self, agent):
        """
        Expande el siguiente nodo en la búsqueda Hill Climbing. Al llegar al objetivo, recalcula el camino óptimo.
        """
        if agent.has_explored:
            # Bomberman sigue el camino óptimo después de recalcularlo
            if agent.optimal_path:
                next_step = agent.optimal_path.pop(0)
                self.current = next_step
                print(f"Moviéndose a {self.current} en el camino óptimo.")
            return

        self.step_count += 1
        print(f"Paso {self.step_count}: Evaluando nodo {self.current}")

        if self.current not in self.visited_nodes:
            cell = agent.model.grid[self.current[0]][self.current[1]]
            if cell is not None:
                cell[0].visit_order = self.step_count
                self.visited_nodes.add(self.current)
                self.path_to_goal.append(self.current)

        agents_in_cell = agent.model.grid[self.current[0]][self.current[1]]
        if any(isinstance(a, GoalAgent) for a in agents_in_cell):
            # Recalcular camino óptimo usando solo nodos expandidos
            agent.path_to_exit = self.calculate_optimal_path(agent)
            agent.optimal_path = agent.path_to_exit[:]
            agent.has_explored = True
            print("Meta alcanzada. Camino óptimo recalculado:", agent.optimal_path)
            return

        neighbors = self.get_neighbors(agent, self.current)
        valid_neighbors = [n for n in neighbors if n not in self.visited_nodes]

        if valid_neighbors:
            next_node = min(valid_neighbors, key=lambda neighbor: self.heuristica(neighbor))
            self.current = next_node
            print(f"Moviendo a {self.current} basado en la heurística")
        else:
            print("No hay vecinos válidos, iniciando retroceso...")
            self.retrogress(agent)

    def calculate_optimal_path(self, agent):
        """
        Calcula el camino óptimo directo desde el nodo inicial hasta el objetivo
        usando solo los nodos expandidos.
        
        Args:
            agent (Agent): Agente Bomberman.

        Returns:
            list: Camino óptimo recalculado desde el inicio hasta el objetivo usando nodos expandidos.
        """
        start = self.path_to_goal[0]  # Nodo inicial
        queue = [(start, [start])]
        visited = set()

        while queue:
            current, path = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            if current == self.goal:
                return path  # Camino directo encontrado

            for neighbor in self.get_neighbors(agent, current):
                if neighbor not in visited and neighbor in self.visited_nodes:
                    queue.append((neighbor, path + [neighbor]))

        return []  # Devuelve un camino vacío si no se encuentra

    def retrogress(self, agent):
        """Retrocede al primer nodo en `path_to_goal` que tenga un vecino válido."""
        for node in self.path_to_goal:
            self.current = node
            neighbors = self.get_neighbors(agent, self.current)
            valid_neighbors = [n for n in neighbors if n not in self.visited_nodes]
            if valid_neighbors:
                next_node = min(valid_neighbors, key=lambda neighbor: self.heuristica(neighbor))
                self.current = next_node
                print(f"Retrocediendo a {self.current} desde nodo {node}")
                self.retrogress_count += 1
                return
        print("No hay más nodos por retroceder. Fin de la búsqueda.")
        self.current = None

    def get_neighbors(self, agent, current):
        """Obtiene los vecinos válidos del nodo actual con prioridad: Izquierda, Arriba, Derecha, Abajo."""
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
        return neighbors  # Devuelve los vecinos válidos
