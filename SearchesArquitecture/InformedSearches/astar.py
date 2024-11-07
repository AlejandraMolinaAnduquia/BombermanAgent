from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
import heapq
import math

class AStarSearch(SearchStrategy):
    """
    Clase que implementa el algoritmo A* para búsqueda de caminos en un entorno de agentes.
    La clase mantiene una cola de prioridad (`open_set`) para expandir nodos en función de
    una heurística, y calcula el costo de la ruta óptima acumulado (`g_score`).
    
    Atributos:
        open_set (list): Cola de prioridad de nodos a expandir.
        visited (set): Conjunto de nodos ya expandidos.
        g_score (dict): Diccionario que almacena el costo acumulado desde el inicio hasta cada nodo.
        step_count (int): Contador de pasos de expansión.
        index (int): Índice para mantener el orden de inserción en la cola de prioridad.
    """

    def __init__(self, heuristic='Manhattan'):
        """
        Inicializa la clase AStarSearch con la heurística seleccionada.
        
        Args:
            heuristic (str): Tipo de heurística, puede ser 'Manhattan' o 'Euclidean'.
        """
        self.open_set = []  # Cola de prioridad que almacena los nodos por expandir.
        self.visited = set()  # Conjunto de nodos que ya fueron expandidos.
        self.g_score = {}  # Diccionario para el costo de movimiento acumulado.
        self.step_count = 0  # Contador de pasos de expansión.
        self.index = 0  # Índice auxiliar para manejar el orden de expansión.
        self.heuristic = heuristic  # Tipo de distancia seleccionada (Manhattan o Euclidean)


    def manhattan_distance(self, pos1, pos2):
        """
        Calcula la distancia de Manhattan entre dos posiciones.

        Args:
            pos1 (tuple): Coordenadas (x, y) del primer punto.
            pos2 (tuple): Coordenadas (x, y) del segundo punto.

        Returns:
            int: Distancia de Manhattan entre las dos posiciones.
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def euclidean_distance(self, pos1, pos2):
        """Calcula la distancia Euclidiana entre dos posiciones."""
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


    def start_search(self, start, goal):
        """
        Inicia la búsqueda A* desde una posición de inicio hasta una posición objetivo.

        Args:
            start (tuple): Coordenadas (x, y) del nodo de inicio.
            goal (tuple): Coordenadas (x, y) del nodo objetivo (meta).

        Funciona reiniciando la cola de prioridad y definiendo el costo acumulado
        para el nodo de inicio.
        """
        self.goal = goal
        self.open_set = []  # Reinicia la cola de prioridad para cada búsqueda.
        start_tuple = (start, [])
        heapq.heappush(self.open_set, (0, self.index, start_tuple[0], [start_tuple[0]]))  # Inserta el nodo inicial.
        self.g_score[start_tuple[0]] = 0  # Inicializa el costo de movimiento del nodo de inicio.
        self.index += 1  # Incrementa el índice para manejo de orden.
        self.step_count = 0  # Resetea el contador de pasos de expansión.

    def explore_step(self, agent, diagonal=False):
        """
        Expande el siguiente nodo en la cola de prioridad y realiza un paso en la búsqueda A*.

        Args:
            agent (Agent): Agente que ejecuta la búsqueda.
            diagonal (bool): Si se permite el movimiento diagonal (por defecto es False).

        Returns:
            tuple or None: La posición actual después de la expansión, o None si se alcanza la meta.
        """
        if not self.open_set:
            return None  # Finaliza si no hay más nodos en la cola de prioridad.

        _, _, current, path = heapq.heappop(self.open_set)
        self.step_count += 1
        print(f"Expandiendo nodo {self.step_count}: {current}, Camino acumulado hasta ahora: {path}")

        # Marca la celda en el orden de expansión para su visualización
        agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count

        agents_in_cell = agent.model.grid[current[0]][current[1]]
        if any(isinstance(a, GoalAgent) for a in agents_in_cell):
            agent.path_to_exit = path
            agent.has_explored = True
            print("Meta alcanzada. Camino óptimo calculado:", path)
            return None

        self.visited.add(current)
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        for direction in directions:
            new_x, new_y = current[0] + direction[0], current[1] + direction[1]
            new_position = (new_x, new_y)

            if (
                0 <= new_x < agent.model.grid.width
                and 0 <= new_y < agent.model.grid.height
                and new_position not in self.visited
            ):
                agents_in_new_cell = agent.model.grid[new_x][new_y]
                if all(isinstance(agent, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for agent in agents_in_new_cell):
                    tentative_g_score = self.g_score[current] + 10

                    # Calcula la heurística según la selección del usuario
                    if self.heuristic == 'Manhattan':
                        h_score = self.manhattan_distance(new_position, self.goal)
                    else:
                        h_score = self.euclidean_distance(new_position, self.goal)
                    
                    f_score = tentative_g_score + h_score

                    if new_position not in self.g_score or tentative_g_score < self.g_score[new_position]:
                        self.g_score[new_position] = tentative_g_score
                        heapq.heappush(self.open_set, (f_score, self.index, new_position, path + [new_position]))
                        self.index += 1

        return current