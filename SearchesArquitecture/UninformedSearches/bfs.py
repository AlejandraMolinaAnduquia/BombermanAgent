from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
from collections import deque

class bfs(SearchStrategy):
    """
    Implementa el algoritmo de Búsqueda en Anchura (BFS), que explora el entorno
    expandiendo cada nodo por niveles, empezando desde el nodo raíz.
    
    Atributos:
        queue (deque): Cola de exploración que almacena los nodos por visitar y sus caminos.
        visited (set): Conjunto de nodos visitados para evitar expansiones redundantes.
        step_count (int): Contador de pasos, usado para marcar el orden de expansión.
    """

    def __init__(self):
        """
        Inicializa la clase BFS con una cola vacía, conjunto de nodos visitados y contador de pasos.
        """
        self.queue = deque()  # Cola de nodos por visitar
        self.visited = set()  # Nodos visitados
        self.step_count = 0  # Contador de pasos de expansión

    def start_search(self, start, goal=None):
        """
        Inicia la búsqueda desde el nodo inicial y añade el primer nodo a la cola.
        
        Args:
            start (tuple): Coordenadas del nodo inicial.
            goal (tuple): Coordenadas del nodo objetivo (opcional).
        
        Almacena el nodo inicial junto con el camino vacío en la cola y lo marca como expandido.
        """
        self.queue.append((start, []))  # Añade el nodo inicial a la cola con un camino vacío
        
        

    def explore_step(self, agent, diagonal=False):
        """
        Expande el siguiente nodo en la cola de BFS, explora sus vecinos y marca los visitados.
        
        Args:
            agent (Agent): Agente que ejecuta la búsqueda en el entorno de modelado.
            diagonal (bool): Indica si la búsqueda permite movimientos diagonales.
        
        Returns:
            current (tuple): Nodo actual que fue expandido, o None si no quedan nodos en la cola.
        """
        if not self.queue:
            return None

        # Extrae el nodo y camino actuales
        current, path = self.queue.popleft()

        # Verifica si el nodo actual es la meta
        agents_in_cell = agent.model.grid[current[0]][current[1]]
        if any(isinstance(a, GoalAgent) for a in agents_in_cell):
            agent.path_to_exit = path
            agent.has_explored = True

            # Marcar la meta como expandida
            agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count
            self.step_count += 1  # Incrementa el contador de pasos
            print("Meta alcanzada y marcada como expandida.")
            return None

        # Expande el nodo si no ha sido visitado
        if current not in self.visited:
            # Marca el nodo con el orden de visita
            agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count
            self.step_count += 1  # Incrementa el contador de pasos
            self.visited.add(current)  # Agrega el nodo al conjunto de visitados

            # Define las direcciones de expansión, con opción de incluir diagonales
            if diagonal:
                directions = [
                    (0, 1), (1, 1), (1, 0), (1, -1),
                    (0, -1), (-1, -1), (-1, 0), (-1, 1)
                ]
            else:
                # Prioridad de direcciones: izquierda, arriba, derecha, abajo
                directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

            # Explora cada dirección para generar nuevos nodos
            for direction in directions:
                new_x, new_y = current[0] + direction[0], current[1] + direction[1]
                new_position = (new_x, new_y)

                # Valida que el nuevo nodo esté dentro de límites y no haya sido visitado
                if (
                    0 <= new_x < agent.model.grid.width
                    and 0 <= new_y < agent.model.grid.height
                    and new_position not in self.visited
                ):
                    agents_in_new_cell = agent.model.grid[new_x][new_y]

                    # Añade el nodo si contiene únicamente agentes válidos (camino, meta, roca, globo)
                    if all(isinstance(a, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for a in agents_in_new_cell):
                        self.queue.append((new_position, path + [new_position]))

        return current  # Devuelve el nodo expandido
