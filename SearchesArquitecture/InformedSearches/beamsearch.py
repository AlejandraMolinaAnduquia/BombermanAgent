from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent

class BeamSearch(SearchStrategy):
    def __init__(self, beam_width=3):
        self.beam_width = beam_width
        self.open_set = []
        self.visited = set()
        self.step_count = 0

    def start_search(self, start, goal):
        """Inicia la búsqueda Beam desde el nodo de inicio."""
        self.goal = goal
        self.open_set = [[start]]  # Inicializa con la posición de inicio
        self.visited = set()  # Reinicia los nodos visitados
        self.step_count = 0  # Resetea el contador de pasos de expansión

    def explore_step(self, agent):
        """Expande el siguiente conjunto de nodos en el haz."""
        if not self.open_set:
            return None

        # Extrae el primer conjunto de caminos del haz
        current_paths = self.open_set.pop(0)
        current = current_paths[-1]  # Última posición del camino

        # Verifica si el nodo actual ya fue visitado
        if current not in self.visited:
            # Marca la celda en el orden de expansión
            self.step_count += 1
            agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count
            print(f"Expandiendo camino {self.step_count}: {current_paths}, Última posición: {current}")

            # Agrega a visitados
            self.visited.add(current)

            # Verifica si el nodo actual es la meta
            agents_in_cell = agent.model.grid[current[0]][current[1]]
            if any(isinstance(a, GoalAgent) for a in agents_in_cell):
                agent.path_to_exit = current_paths
                agent.has_explored = True
                print("Meta alcanzada. Camino óptimo calculado:", current_paths)
                return None

            # Genera nuevos caminos a partir del nodo actual
            new_paths = []
            directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Direcciones ortogonales

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
                        new_paths.append(current_paths + [new_position])

            # Limita a los mejores caminos según el ancho del haz
            self.open_set.extend(sorted(new_paths, key=lambda p: self.evaluate_path(p))[:self.beam_width])

        return current

    def evaluate_path(self, path):
        """Evaluar un camino según una heurística (por ejemplo, longitud del camino)."""
        # Aquí puedes implementar la lógica para evaluar los caminos
        return len(path)
