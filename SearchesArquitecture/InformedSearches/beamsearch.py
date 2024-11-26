from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
import math

class BeamSearch(SearchStrategy):
    """
    Implementación del algoritmo Beam Search con capacidad para evaluar caminos mediante 
    heurísticas de Manhattan o Euclídea en un entorno de agentes. El haz limita el número 
    de caminos a explorar en cada paso.
    """

    def __init__(self, beam_width=3, heuristic='Manhattan'):
        """
        Inicializa la clase BeamSearch con el ancho de haz y la heurística seleccionados.
        
        Args:
            beam_width (int): Número máximo de caminos permitidos en cada expansión.
            heuristic (str): Tipo de heurística a usar, puede ser 'Manhattan' o 'Euclidean'.
        """
        self.beam_width = beam_width  # Limita el número de caminos a explorar en cada paso
        self.open_set = []  # Lista que almacena los caminos en el haz actual
        self.visited = set()  # Conjunto de nodos ya explorados
        self.step_count = 0  # Contador de pasos de expansión
        self.heuristic = heuristic  # Heurística de elección: Manhattan o Euclidean

    def start_search(self, start, goal):
        """
        Inicializa la búsqueda, configurando el punto de inicio y la meta.
        
        Args:
            start (tuple): Posición de inicio (x, y).
            goal (tuple): Posición de la meta (x, y).
        """
        self.goal = goal
        self.open_set = [[start]]  # Inicializa el open_set con el camino desde el nodo de inicio
        self.visited = set()  # Reinicia el conjunto de nodos visitados
        self.step_count = 0  # Reinicia el contador de pasos de expansión

    def manhattan_distance(self, pos1, pos2):
        """
        Calcula la distancia Manhattan entre dos posiciones.
        
        Args:
            pos1 (tuple): Primera posición (x, y).
            pos2 (tuple): Segunda posición (x, y).
        
        Returns:
            int: Distancia Manhattan entre pos1 y pos2.
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def euclidean_distance(self, pos1, pos2):
        """
        Calcula la distancia Euclidiana entre dos posiciones.
        
        Args:
            pos1 (tuple): Primera posición (x, y).
            pos2 (tuple): Segunda posición (x, y).
        
        Returns:
            float: Distancia Euclidiana entre pos1 y pos2.
        """
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def explore_step(self, agent):
        """
        Realiza un paso de expansión de caminos en el haz, generando nuevos caminos y evaluando
        cada uno para continuar solo con los mejores.

        Args:
            agent: El agente que ejecuta la búsqueda.
        
        Returns:
            list or None: Devuelve el primer camino en el open_set si no se alcanza la meta.
        """
        if not self.open_set:
            return None

        # Lista para almacenar los nuevos caminos generados
        new_paths = []
        for path in self.open_set:
            current = path[-1]  # Último nodo en el camino actual

            # Si el nodo actual no ha sido visitado, se marca como visitado y se expande
            if current not in self.visited:
                self.visited.add(current)  # Marcar el nodo como visitado
                self.step_count += 1
                agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count
                print(f"Expandiendo camino {self.step_count}: {path}, Última posición: {current}")

                # Comprobar si el nodo actual contiene la meta
                agents_in_cell = agent.model.grid[current[0]][current[1]]
                if any(isinstance(a, GoalAgent) for a in agents_in_cell):
                    agent.path_to_exit = path
                    agent.has_explored = True
                    print("Meta alcanzada. Camino óptimo calculado:", path)
                    return None

                # Generar vecinos válidos y extender el camino actual
                neighbors = self.get_neighbors(agent, current)
                for neighbor in neighbors:
                    # Solo se añade un vecino si no se ha visitado (evita ciclos)
                    if neighbor not in self.visited:
                        new_paths.append(path + [neighbor])  # Añadir nuevo camino extendido

        # Ordena los nuevos caminos según la heurística seleccionada y limita el open_set
        self.open_set = sorted(new_paths, key=lambda p: self.evaluate_path(p))[:self.beam_width]
        
        # Retorna el primer camino en open_set si hay caminos restantes
        return self.open_set[0] if self.open_set else None

    def get_neighbors(self, agent, current):
        """
        Obtiene los vecinos válidos del nodo actual con una prioridad de movimientos:
        Izquierda, Arriba, Derecha, Abajo.
        
        Args:
            agent: El agente que realiza la búsqueda.
            current (tuple): Nodo actual (x, y).
        
        Returns:
            list: Lista de vecinos válidos.
        """
        neighbors = []
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Prioridad de movimiento
        for direction in directions:
            new_x, new_y = current[0] + direction[0], current[1] + direction[1]
            new_position = (new_x, new_y)

            # Verifica que el vecino esté dentro de los límites del mapa
            if (
                0 <= new_x < agent.model.grid.width
                and 0 <= new_y < agent.model.grid.height
            ):
                agents_in_new_cell = agent.model.grid[new_x][new_y]
                # Agrega el vecino si es una celda transitable
                if all(isinstance(agent, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for agent in agents_in_new_cell):
                    neighbors.append(new_position)
        return neighbors

    def evaluate_path(self, path):
        """
        Evalúa el camino según la distancia Manhattan o Euclidiana, basándose en la heurística.
        
        Args:
            path (list): Lista de nodos que conforman el camino a evaluar.
        
        Returns:
            float or int: Valor heurístico del camino.
        """
        if self.heuristic == 'Manhattan':
            return self.manhattan_distance(path[-1], self.goal)
        elif self.heuristic == 'Euclidean':
            return self.euclidean_distance(path[-1], self.goal)
        else:
            raise ValueError("Heurística no válida. Use 'Manhattan' o 'Euclidean'.")
