from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.metal import MetalAgent
from AgentArquitecture.globe import GlobeAgent

class HillClimbing(SearchStrategy):
    """
    Implementa el algoritmo de Hill Climbing con retroceso. Este enfoque selecciona en cada paso el vecino
    que maximiza la heurística (distancia de Manhattan al objetivo), y retrocede si no encuentra una mejor opción.
    
    Atributos:
        step_count (int): Número de pasos de expansión, usado para visualizar el progreso.
        visited_nodes (set): Conjunto de nodos ya visitados.
        path_to_goal (list): Lista de nodos en el camino explorado hasta el momento.
        current (tuple): Nodo actual en el proceso de exploración.
        goal (tuple): Nodo objetivo de la búsqueda.
    """

    def __init__(self):
        """
        Inicializa los atributos necesarios para la búsqueda Hill Climbing.
        """
        self.step_count = 0  # Contador de pasos para visualizar el orden de expansión
        self.visited_nodes = set()  # Conjunto de nodos visitados
        self.path_to_goal = []  # Camino actual explorado
        self.current = None  # Nodo actual
        self.goal = None  # Nodo objetivo

    def start_search(self, start, goal):
        """
        Inicia la búsqueda Hill Climbing desde el nodo de inicio hacia el objetivo.
        
        Args:
            start (tuple): Coordenadas del nodo de inicio.
            goal (tuple): Coordenadas del nodo objetivo.
        
        Este método reinicia los contadores, el nodo actual, y el camino explorado.
        """
        self.goal = goal
        self.current = start  # Define el nodo inicial como actual
        self.step_count = 0  # Resetea el contador de pasos
        self.visited_nodes.clear()  # Limpia el conjunto de nodos visitados
        self.path_to_goal.clear()  # Reinicia el camino almacenado

    def heuristic(self, position):
        """
        Calcula la heurística para un nodo dado: la distancia de Manhattan al objetivo.
        
        Args:
            position (tuple): Coordenadas del nodo actual.
        
        Returns:
            int: Distancia de Manhattan desde el nodo actual hasta el nodo objetivo.
        """
        return abs(position[0] - self.goal[0]) + abs(position[1] - self.goal[1])

    def explore_step(self, agent):
        """
        Expande el siguiente nodo en la búsqueda Hill Climbing con retroceso. Evalúa vecinos y retrocede si necesario.
        
        Args:
            agent (Agent): Agente que ejecuta la búsqueda en el entorno de modelado.
        
        Returns:
            None
        """
        self.step_count += 1
        print(f"Paso {self.step_count}: Evaluando nodo {self.current}")

        # Valida el nodo actual y lo marca como visitado si es necesario
        if self.current is None or not (0 <= self.current[0] < agent.model.grid.width) or not (0 <= self.current[1] < agent.model.grid.height):
            print("Nodo actual no válido:", self.current)
            return None

        if self.current not in self.visited_nodes:
            # Marca el nodo con el orden de visita y lo agrega al conjunto de nodos visitados
            cell = agent.model.grid[self.current[0]][self.current[1]]
            if cell is not None:
                cell[0].visit_order = self.step_count  # Marca el nodo con el orden de visita
                self.visited_nodes.add(self.current)  # Añade el nodo a visitados
                self.path_to_goal.append(self.current)  # Añade el nodo al camino

        # Verifica si el nodo actual es la meta
        agents_in_cell = agent.model.grid[self.current[0]][self.current[1]]
        if any(isinstance(a, GoalAgent) for a in agents_in_cell):
            agent.path_to_exit = self.path_to_goal
            agent.has_explored = True
            print("Meta alcanzada en:", self.current)
            return None

        # Genera vecinos válidos del nodo actual
        neighbors = self.get_neighbors(agent, self.current)
        valid_neighbors = []
        for neighbor in neighbors:
            agents_at_neighbor = agent.model.grid[neighbor[0]][neighbor[1]]
            if neighbor not in self.visited_nodes:
                if any(isinstance(a, MetalAgent) for a in agents_at_neighbor):
                    continue  # Omite vecinos bloqueados por MetalAgent
                else:
                    valid_neighbors.append(neighbor)  # Agrega vecinos válidos

        if valid_neighbors:
            # Selecciona el vecino con la menor heurística (más cercano al objetivo)
            next_node = min(valid_neighbors, key=lambda neighbor: self.heuristic(neighbor))
            self.current = next_node  # Actualiza el nodo actual al mejor vecino
            print(f"Moviendo a {self.current} basado en la heurística")
        else:
            # Retrocede si no hay vecinos válidos
            print("No hay vecinos válidos, iniciando retroceso...")
            if self.path_to_goal:
                self.path_to_goal.pop()  # Elimina el último nodo del camino
                if self.path_to_goal:
                    self.current = self.path_to_goal[-1]  # Retrocede al nodo anterior
                    print(f"Retrocediendo a {self.current}")
                else:
                    print("No hay más nodos por retroceder. Fin de la búsqueda.")
                    self.current = None
            else:
                print("Retroceso imposible, ningún camino alternativo disponible.")
                self.current = None

        return None

    def get_neighbors(self, agent, current):
        """
        Obtiene los vecinos válidos (caminos, rocas, globos, y el objetivo) del nodo actual.
        
        Args:
            agent (Agent): Agente que ejecuta la búsqueda en el entorno de modelado.
            current (tuple): Coordenadas del nodo actual.
        
        Returns:
            list: Lista de posiciones vecinas válidas.
        """
        neighbors = []

        # Prioridad: Izquierda, arriba, derecha, abajo
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Direcciones ortogonales


        for direction in directions:
            new_x, new_y = current[0] + direction[0], current[1] + direction[1]
            new_position = (new_x, new_y)

            if (
                0 <= new_x < agent.model.grid.width
                and 0 <= new_y < agent.model.grid.height
            ):
                # Solo incluye posiciones con caminos, rocas, globos o el objetivo
                agents_in_new_cell = agent.model.grid[new_x][new_y]
                if all(isinstance(agent, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for agent in agents_in_new_cell):
                    neighbors.append(new_position)

        return neighbors  # Devuelve los vecinos válidos
