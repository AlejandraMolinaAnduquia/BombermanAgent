from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent

class dfs(SearchStrategy):
    """
    Implementa el algoritmo de Búsqueda en Profundidad (DFS) para explorar nodos en un entorno de agente.
    
    Atributos:
        stack (list): Pila de exploración que almacena nodos y caminos acumulados.
        visited (set): Conjunto de nodos visitados para evitar expandir nodos repetidos.
        step_count (int): Contador de pasos para registrar el orden de expansión.
        goal (tuple): Coordenadas de la meta, si están definidas.
    """

    def __init__(self):
        """
        Inicializa DFS con una pila vacía, conjunto de nodos visitados y un contador de pasos.
        """
        self.stack = []  # Pila de nodos pendientes de exploración
        self.visited = set()  # Conjunto de nodos visitados
        self.step_count = 0  # Contador para marcar el orden de visita
        self.goal = None  # Posición de la meta

    def start_search(self, start, goal=None):
        """
        Inicia la búsqueda DFS desde el nodo inicial, y establece la meta.
        
        Args:
            start (tuple): Coordenadas del nodo inicial.
            goal (tuple, opcional): Coordenadas del nodo objetivo, si existen.
        
        Agrega la posición inicial y el camino vacío a la pila y define la meta.
        """
        self.stack.append((start, [start]))  # Inicializa la pila con el nodo de inicio y su camino
        self.goal = goal  # Almacena la meta si se proporciona

    def explore_step(self, agent, diagonal=False):
        """
        Expande el siguiente nodo en la pila de DFS, y marca el camino al nodo.
        
        Args:
            agent (Agent): Agente que ejecuta la búsqueda en el entorno.
            diagonal (bool): Indica si la búsqueda permite movimientos diagonales.
        
        Returns:
            current (tuple): Nodo actual expandido, o None si no quedan nodos en la pila.
        """
        if not self.stack:
            return None

        # Extrae el nodo y camino actuales de la pila
        current, path = self.stack.pop()

        # Verifica si el nodo actual es la meta
        AgentArquitecture_in_cell = agent.model.grid[current[0]][current[1]]
        if self.goal is not None and any(isinstance(a, GoalAgent) for a in AgentArquitecture_in_cell):
            agent.path_to_exit = path
            agent.has_explored = True
            return None

        # Expande el nodo si no ha sido visitado
        if current not in self.visited:
            # Marca el nodo con el orden de visita
            agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count
            self.step_count += 1  # Incrementa el contador de pasos
            self.visited.add(current)  # Añade el nodo al conjunto de visitados

            # Define direcciones de expansión, con opción de incluir diagonales
            if diagonal:
                directions = [
                    (0, 1), (1, 1), (1, 0), (1, -1),
                    (0, -1), (-1, -1), (-1, 0), (-1, 1)
                ]
            else:
                directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

            directions.reverse()  # Invierte el orden para mantener el comportamiento LIFO

            # Explora cada dirección para generar nuevos nodos
            for direction in directions:
                new_x, new_y = current[0] + direction[0], current[1] + direction[1]
                new_position = (new_x, new_y)

                # Valida que el nuevo nodo esté dentro de los límites y no haya sido visitado
                if (
                    0 <= new_x < agent.model.grid.width
                    and 0 <= new_y < agent.model.grid.height
                    and new_position not in self.visited
                ):
                    AgentArquitecture_in_new_cell = agent.model.grid[new_x][new_y]

                    # Solo se añaden nodos que contienen agentes RoadAgent, GoalAgent, RockAgent, GlobeAgent
                    if all(isinstance(a, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for a in AgentArquitecture_in_new_cell):
                        self.stack.append((new_position, path + [new_position]))

        return current  # Devuelve el nodo expandido
