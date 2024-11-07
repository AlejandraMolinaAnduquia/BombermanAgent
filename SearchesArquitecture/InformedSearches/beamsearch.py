from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent

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

    def __init__(self, beam_width=3):
        """
        Inicializa la búsqueda en haz con un ancho especificado.
        
        Args:
            beam_width (int): Número de caminos a mantener en la exploración en cada paso.
        """
        self.beam_width = beam_width  # Número máximo de caminos a explorar por paso
        self.open_set = []  # Lista de caminos en el haz actual
        self.visited = set()  # Nodos ya explorados
        self.step_count = 0  # Contador de pasos de expansión

    def start_search(self, start, goal):
        """
        Inicia la búsqueda en haz desde una posición de inicio hacia un objetivo.
        
        Args:
            start (tuple): Coordenadas de inicio (x, y).
            goal (tuple): Coordenadas de la meta (x, y).
        
        Este método reinicia la lista de rutas (open_set) con la posición inicial y limpia
        el conjunto de nodos visitados.
        """
        self.goal = goal
        self.open_set = [[start]]  # Inicializa el haz con un camino que contiene solo el nodo de inicio
        self.visited = set()  # Reinicia los nodos visitados
        self.step_count = 0  # Reinicia el contador de pasos de expansión

    def explore_step(self, agent):
        """
        Expande el siguiente conjunto de nodos en el haz, siguiendo la estrategia de mantener solo
        los mejores caminos según el ancho del haz.
        
        Args:
            agent (Agent): Agente que ejecuta la búsqueda en el entorno de modelado.
        
        Returns:
            tuple or None: La posición actual expandida o None si se ha alcanzado el objetivo.
        """
        if not self.open_set:
            return None  # Si no quedan caminos, finaliza la búsqueda

        # Extrae el primer camino del haz
        current_paths = self.open_set.pop(0)
        current = current_paths[-1]  # Última posición del camino actual

        # Verifica si el nodo actual no ha sido visitado
        if current not in self.visited:
            # Marca la celda en el orden de expansión para visualización
            self.step_count += 1
            agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count
            print(f"Expandiendo camino {self.step_count}: {current_paths}, Última posición: {current}")

            # Marca el nodo como visitado
            self.visited.add(current)

            # Verifica si se ha alcanzado el objetivo
            agents_in_cell = agent.model.grid[current[0]][current[1]]
            if any(isinstance(a, GoalAgent) for a in agents_in_cell):
                agent.path_to_exit = current_paths
                agent.has_explored = True
                print("Meta alcanzada. Camino óptimo calculado:", current_paths)
                return None  # Termina si se alcanza el objetivo

            # Genera nuevas rutas a partir de la posición actual en todas las direcciones ortogonales
            new_paths = []
            directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Direcciones ortogonales

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
                    # Solo permite avanzar sobre caminos, rocas y la meta
                    if all(isinstance(agent, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for agent in agents_in_new_cell):
                        new_paths.append(current_paths + [new_position])

            # Agrega solo los mejores caminos según el ancho del haz
            self.open_set.extend(sorted(new_paths, key=lambda p: self.evaluate_path(p))[:self.beam_width])

        return current  # Devuelve la posición actual si no ha alcanzado la meta

    def evaluate_path(self, path):
        """
        Evalúa un camino según su longitud (por defecto, la longitud más corta se considera mejor).
        
        Args:
            path (list): Lista de posiciones que componen el camino.
        
        Returns:
            int: Valor heurístico del camino, en este caso, su longitud.
        """
        return len(path)  # La evaluación predeterminada es la longitud del camino
