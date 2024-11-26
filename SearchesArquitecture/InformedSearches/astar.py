from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
import heapq
import math

class AStarSearch(SearchStrategy):
    """
    Implementación del algoritmo A* para búsqueda de caminos en un entorno de agentes.
    Este algoritmo utiliza una heurística para calcular el costo total estimado (f_score) y
    selecciona el nodo más prometedor en cada expansión hasta encontrar el objetivo.
    
    Atributos:
        open_set (list): Cola de prioridad de nodos a expandir.
        visited (set): Conjunto de nodos ya expandidos.
        g_score (dict): Costos acumulados desde el inicio hasta cada nodo.
        f_score (dict): Costos totales estimados (g_score + heurística) de cada nodo.
        step_count (int): Contador de pasos de expansión para visualización.
        index (int): Índice para el orden de expansión.
        heuristic (str): Heurística seleccionada ('Manhattan' o 'Euclidean').
        weight (float): Factor de ponderación para la heurística.
    """

    def __init__(self, heuristic='Manhattan'):
        """
        Inicializa el algoritmo A* con los atributos necesarios.
        
        Args:
            heuristic (str): Tipo de heurística ('Manhattan' o 'Euclidean').
        """
        self.open_set = []     # Cola de prioridad para nodos pendientes de expansión
        self.visited = set()   # Conjunto de nodos ya visitados
        self.g_score = {}      # Costos acumulados hasta cada nodo
        self.f_score = {}      # Costos totales estimados (g_score + heurística)
        self.step_count = 0    # Contador de pasos para orden de expansión
        self.index = 0         # Índice para mantener el orden en la cola de prioridad
        self.heuristic = heuristic
        self.weight = 1.0      # Peso de la heurística para ajustar la función de evaluación

    def manhattan_distance(self, pos1, pos2):
        """
        Calcula la distancia de Manhattan entre dos posiciones.
        
        Args:
            pos1, pos2 (tuple): Coordenadas de las posiciones (x, y).
        
        Returns:
            int: Distancia de Manhattan entre las dos posiciones.
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def euclidean_distance(self, pos1, pos2):
        """
        Calcula la distancia Euclidiana entre dos posiciones.
        
        Args:
            pos1, pos2 (tuple): Coordenadas de las posiciones (x, y).
        
        Returns:
            float: Distancia Euclidiana entre las dos posiciones.
        """
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def start_search(self, start, goal):
        """
        Inicializa la búsqueda A* estableciendo el nodo de inicio y el nodo objetivo,
        así como los valores de los puntajes g y f para el nodo inicial.
        
        Args:
            start (tuple): Coordenadas del nodo de inicio.
            goal (tuple): Coordenadas del nodo objetivo.
        """
        self.goal = goal
        self.open_set = []
        self.visited.clear()
        self.g_score.clear()
        self.f_score.clear()
        
        # Configurar puntajes g y f para el nodo inicial
        self.g_score[start] = 0
        h_score = self.manhattan_distance(start, goal) if self.heuristic == 'Manhattan' else self.euclidean_distance(start, goal)
        h_score *= self.weight  # Aplicar peso a la heurística
        self.f_score[start] = h_score
        
        # Añadir el nodo inicial a la cola de prioridad
        heapq.heappush(self.open_set, (h_score, 0, self.index, start, [start]))
        self.step_count = 0  # Restablece el contador de pasos de expansión

    def is_valid_move(self, pos, agent):
        """
        Determina si un movimiento a una posición específica es válido, verificando
        los límites del mapa y la presencia de agentes permitidos en esa celda.
        
        Args:
            pos (tuple): Coordenadas de la posición a verificar.
            agent (Agent): Agente que ejecuta la búsqueda en el entorno.
        
        Returns:
            bool: `True` si el movimiento es válido, `False` en caso contrario.
        """
        x, y = pos
        # Verifica si la posición está dentro de los límites de la cuadrícula
        if not (0 <= x < agent.model.grid.width and 0 <= y < agent.model.grid.height):
            return False
            
        agents_in_cell = agent.model.grid[x][y]
        # Solo permite movimiento sobre agentes válidos (camino, meta, roca, globo)
        return all(isinstance(a, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for a in agents_in_cell)

    def get_neighbors(self, pos):
        """
        Genera las posiciones vecinas de un nodo en el orden de preferencia.
        
        Args:
            pos (tuple): Coordenadas del nodo actual.
        
        Returns:
            list: Lista de posiciones vecinas en el orden de expansión (arriba, derecha, abajo, izquierda).
        """
        x, y = pos
        return [
            (x-1, y),  # Arriba
            (x, y+1),  # Derecha
            (x+1, y),  # Abajo
            (x, y-1)   # Izquierda
        ]

    def explore_step(self, agent, diagonal=False):
        """
        Expande el nodo con el puntaje f más bajo de la cola de prioridad. Marca el nodo como expandido
        y, si se encuentra el objetivo, termina la búsqueda. De lo contrario, evalúa vecinos.
        
        Args:
            agent (Agent): Agente que ejecuta la búsqueda en el entorno de modelado.
            diagonal (bool): Indicador para movimientos diagonales (no utilizado en esta implementación).
        
        Returns:
            tuple or None: La posición actual expandida o None si se ha alcanzado el objetivo.
        """
        if not self.open_set:
            return None  # Termina si no hay nodos por expandir

        # Extrae el nodo con el puntaje f más bajo
        _, g_score, _, current, path = heapq.heappop(self.open_set)
        
        # Omite el nodo si ya fue visitado
        if current in self.visited:
            return current

        # Incrementa el contador de pasos y marca el nodo en la interfaz
        self.step_count += 1
        print(f"Expandiendo nodo {self.step_count}: {current}, Camino acumulado hasta ahora: {path}")
        
        # Marcar el nodo como expandido para la visualización en la interfaz
        agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count
        self.visited.add(current)

        agents_in_cell = agent.model.grid[current[0]][current[1]]
        
        # Si el nodo actual es la meta, marca la meta como expandida y termina la búsqueda
        if any(isinstance(a, GoalAgent) for a in agents_in_cell):
            agent.model.grid[self.goal[0]][self.goal[1]][0].visit_order = self.step_count  # Marca la salida como expandida
            agent.path_to_exit = path  # Guarda el camino óptimo encontrado
            agent.has_explored = True  # Indica que la búsqueda ha terminado
            print("Meta alcanzada y marcada como expandida. Camino óptimo calculado:", path)
            return None

        # Expande los vecinos en el orden especificado
        for next_pos in self.get_neighbors(current):
            if not self.is_valid_move(next_pos, agent) or next_pos in self.visited:
                continue  # Omite movimientos no válidos o ya visitados

            tentative_g_score = g_score + 1  # Calcula el puntaje g tentativo

            # Solo actualiza los puntajes g y f si se mejora el puntaje g
            if next_pos not in self.g_score or tentative_g_score < self.g_score[next_pos]:
                self.g_score[next_pos] = tentative_g_score
                h_score = (self.manhattan_distance(next_pos, self.goal) 
                          if self.heuristic == 'Manhattan' 
                          else self.euclidean_distance(next_pos, self.goal))
                h_score *= self.weight  # Aplicar peso a la heurística
                
                f_score = tentative_g_score + h_score  # Calcula el puntaje f
                self.f_score[next_pos] = f_score
                
                self.index += 1
                # Añade el vecino a la cola de prioridad con el nuevo puntaje f
                heapq.heappush(self.open_set, (f_score, tentative_g_score, self.index, next_pos, path + [next_pos]))

        return current  # Devuelve la posición actual si no se alcanzó la meta
