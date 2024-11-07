from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
import heapq

class ucs(SearchStrategy):
    """
    Implementación de la búsqueda de costo uniforme (UCS) para encontrar el camino más barato
    hacia un objetivo en un entorno de agente.

    Atributos:
        priority_queue (list): Cola de prioridad que almacena nodos, costes acumulados y caminos.
        visited (set): Conjunto de nodos visitados para evitar expandir nodos repetidos.
        cost_so_far (dict): Diccionario que almacena el costo mínimo acumulado hacia cada nodo.
        step_count (int): Contador de pasos para registrar el orden de expansión de nodos.
        index (int): Contador para mantener el orden de inserción en la cola de prioridad.
    """

    def __init__(self):
        """
        Inicializa UCS con una cola de prioridad vacía, conjunto de nodos visitados, y costo acumulado.
        """
        self.priority_queue = []  # Cola de prioridad para nodos pendientes de expansión
        self.visited = set()  # Nodos ya explorados
        self.cost_so_far = {}  # Costo acumulado hacia cada nodo
        self.step_count = 0  # Contador para marcar el orden de visita
        self.index = 0  # Contador para el orden en la cola de prioridad

    def start_search(self, start, goal=None):
        """
        Inicia la búsqueda UCS desde el nodo inicial y establece el nodo objetivo.

        Args:
            start (tuple): Coordenadas del nodo inicial.
            goal (tuple, opcional): Coordenadas del nodo objetivo, si existe.

        Inicializa el costo del nodo inicial en 0 y lo agrega a la cola de prioridad.
        """
        # Verifica que el nodo inicial tenga coordenadas válidas
        if isinstance(start, tuple) and len(start) >= 2:
            start_position = (start[0], start[1])  # Coordenadas iniciales
        else:
            raise ValueError("El parámetro 'start' debe ser una tupla con al menos dos elementos.")

        # Añade el nodo inicial a la cola de prioridad con costo 0
        heapq.heappush(self.priority_queue, (0, self.index, start_position, [start_position]))
        self.cost_so_far[start_position] = 0
        self.index += 1
        
        # Define el objetivo si se proporciona
        self.goal = goal if goal is not None else None

    def explore_step(self, agent, diagonal=False):
        """
        Expande el siguiente nodo en la cola de prioridad y marca el camino al nodo.

        Args:
            agent (Agent): Agente que ejecuta la búsqueda en el entorno.
            diagonal (bool): Indica si la búsqueda permite movimientos diagonales.

        Returns:
            current (tuple): Nodo actual expandido o None si no quedan nodos en la cola de prioridad.
        """
        if not self.priority_queue:
            return None

        # Extrae el nodo con el menor costo acumulado
        current_cost, _, current, path = heapq.heappop(self.priority_queue)

        # Verifica si el nodo contiene el objetivo
        AgentArquitecture_in_cell = agent.model.grid[current[0]][current[1]]
        if any(isinstance(a, GoalAgent) for a in AgentArquitecture_in_cell):
            agent.path_to_exit = path
            agent.has_explored = True
            return None

        # Marca el nodo actual si no ha sido visitado
        if current not in self.visited:
            # Marca el orden de visita en el nodo
            agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count
            self.step_count += 1
            self.visited.add(current)

            # Define las direcciones de expansión, incluyendo diagonales si está habilitado
            if diagonal:
                directions = [
                    (0, 1, False), (1, 1, True), (1, 0, False), (1, -1, True),
                    (0, -1, False), (-1, -1, True), (-1, 0, False), (-1, 1, True)
                ]
            else:
                directions = [(-1, 0, False), (0, 1, False), (1, 0, False), (0, -1, False)]

            # Expande cada dirección
            for direction in directions:
                new_x, new_y, is_diagonal = current[0] + direction[0], current[1] + direction[1], direction[2]
                new_position = (new_x, new_y)

                # Verifica que el nuevo nodo esté dentro de los límites y no haya sido visitado
                if (
                    0 <= new_x < agent.model.grid.width
                    and 0 <= new_y < agent.model.grid.height
                    and new_position not in self.visited
                ):
                    AgentArquitecture_in_new_cell = agent.model.grid[new_x][new_y]

                    # Permite solo nodos de tipo RoadAgent, GoalAgent, RockAgent, GlobeAgent
                    if all(isinstance(a, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for a in AgentArquitecture_in_new_cell):
                        # Calcula el nuevo costo acumulado al nodo vecino
                        new_cost = current_cost + (13 if is_diagonal else 10)
                        if new_position not in self.cost_so_far or new_cost < self.cost_so_far[new_position]:
                            self.cost_so_far[new_position] = new_cost
                            heapq.heappush(self.priority_queue, (new_cost, self.index, new_position, path + [new_position]))
                            self.index += 1

        return current  # Devuelve el nodo expandido
