from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
import math

class BeamSearch(SearchStrategy):
    """
    Implementación de la búsqueda en haz (Beam Search). Este método explora solo un número
    limitado de rutas posibles (determinado por `beam_width`), lo que permite reducir el
    espacio de búsqueda a cambio de una menor exhaustividad.
    
    Atributos:
        beam_width (int): Número de rutas a expandir en cada paso.
        open_set (list): Lista de rutas actualmente en consideración.
        visited (set): Conjunto de nodos que ya fueron expandidos.
        step_count (int): Contador de pasos de expansión, para visualizar el progreso.
    """

    def __init__(self, beam_width=3, heuristic='Manhattan'):
        """
        Inicializa la búsqueda en haz con un ancho especificado y la heurística elegida.
        
        Args:
            beam_width (int): Número de caminos a mantener en la exploración en cada paso.
            heuristic (str): Tipo de heurística, puede ser 'Manhattan' o 'Euclidean'.
        """
        self.beam_width = beam_width  # Número máximo de caminos a explorar por paso
        self.open_set = []  # Lista de caminos en el haz actual
        self.visited = set()  # Nodos ya explorados
        self.step_count = 0  # Contador de pasos de expansión
        self.heuristic = heuristic  # Heurística seleccionada para evaluar caminos

    def start_search(self, start, goal):
        """
        Inicia la búsqueda en haz desde una posición de inicio hacia un objetivo.
        
        Args:
            start (tuple): Coordenadas de inicio (x, y).
            goal (tuple): Coordenadas de la meta (x, y).
        """
        self.goal = goal
        self.open_set = [[start]]  # Inicializa el haz con un camino que contiene solo el nodo de inicio
        self.visited = set()  # Reinicia los nodos visitados
        self.step_count = 0  # Reinicia el contador de pasos de expansión

    def manhattan_distance(self, pos1, pos2):
        """Calcula la distancia de Manhattan entre dos posiciones."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def euclidean_distance(self, pos1, pos2):
        """Calcula la distancia Euclidiana entre dos posiciones."""
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def explore_step(self, agent):
        """Expande el siguiente conjunto de nodos en el haz, manteniendo solo los mejores caminos según el ancho del haz."""
        if not self.open_set:
            return None  # Si no quedan caminos, finaliza la búsqueda

        # Extrae el primer camino del haz
        current_paths = self.open_set.pop(0)
        current = current_paths[-1]  # Última posición del camino actual

        if current not in self.visited:
            # Marca el nodo actual como visitado
            self.visited.add(current)
            self.step_count += 1
            agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count
            print(f"Expandiendo camino {self.step_count}: {current_paths}, Última posición: {current}")

            # Verifica si se ha alcanzado el objetivo
            agents_in_cell = agent.model.grid[current[0]][current[1]]
            if any(isinstance(a, GoalAgent) for a in agents_in_cell):
                agent.path_to_exit = current_paths
                agent.has_explored = True
                print("Meta alcanzada. Camino óptimo calculado:", current_paths)
                return None

            # Genera nuevas rutas a partir de la posición actual en la prioridad especificada
            new_paths = []
            directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Prioridad: Izquierda, Arriba, Derecha, Abajo

            for direction in directions:
                new_x, new_y = current[0] + direction[0], current[1] + direction[1]
                new_position = (new_x, new_y)

                # Verifica límites del mapa y que la posición no esté visitada
                if (
                    0 <= new_x < agent.model.grid.width
                    and 0 <= new_y < agent.model.grid.height
                    and new_position not in self.visited
                ):
                    agents_in_new_cell = agent.model.grid[new_x][new_y]
                    if all(isinstance(agent, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for agent in agents_in_new_cell):
                        new_paths.append(current_paths + [new_position])

            # Agrega solo los mejores caminos según el ancho del haz
            self.open_set.extend(sorted(new_paths, key=lambda p: self.evaluate_path(p))[:self.beam_width])

        return current  # Devuelve la posición actual si no ha alcanzado la meta

    def retrogress(self, agent):
        """
        Realiza el retroceso empezando por el primer nodo expandido en `path_to_exit` que tenga un vecino válido.
        Si el primer nodo no tiene vecinos válidos, intenta con el segundo y así sucesivamente.
        """
        for index, node in enumerate(agent.path_to_exit):
            self.current = node
            neighbors = self.get_neighbors(agent, node)
            valid_neighbors = [n for n in neighbors if n not in self.visited]

            if valid_neighbors:
                next_node = min(valid_neighbors, key=lambda neighbor: self.evaluate_path([neighbor]))
                self.current = next_node
                print(f"Retrocediendo a {self.current} desde el nodo {node}")
                return
        print("No hay más nodos por retroceder. Fin de la búsqueda.")
        self.current = None

    def get_neighbors(self, agent, current):
        """
        Obtiene los vecinos válidos del nodo actual con prioridad: Izquierda, Arriba, Derecha, Abajo.
        """
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

    def evaluate_path(self, path):
        """
        Evalúa un camino usando la heurística seleccionada para el objetivo.
        
        Args:
            path (list): Lista de posiciones en el camino actual.
        
        Returns:
            float: Valor heurístico del camino (más bajo es mejor).
        """
        return self.manhattan_distance(path[-1], self.goal) if self.heuristic == 'Manhattan' else self.euclidean_distance(path[-1], self.goal)
