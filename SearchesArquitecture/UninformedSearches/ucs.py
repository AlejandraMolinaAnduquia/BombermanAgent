from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
import heapq

class ucs(SearchStrategy):
    def __init__(self):
        self.priority_queue = []
        self.visited = set()
        self.cost_so_far = {}
        self.step_count = 0
        self.index = 0

    def start_search(self, start, goal=None):
        # Aseguramos que `start` sea una tupla con al menos un elemento
        if isinstance(start, tuple) and len(start) >= 2:
            start_position = (start[0], start[1])  # Asumiendo que start[0] son las coordenadas x y start[1] y
        else:
            raise ValueError("El parámetro 'start' debe ser una tupla con al menos dos elementos.")

        heapq.heappush(self.priority_queue, (0, self.index, start_position, [start_position]))
        self.cost_so_far[start_position] = 0
        self.index += 1
        
        # Manejo del objetivo
        if goal is not None:
            self.goal = goal
        else:
            self.goal = None

    def explore_step(self, agent, diagonal=False):
        if not self.priority_queue:
            return None

        current_cost, _, current, path = heapq.heappop(self.priority_queue)

        AgentArquitecture_in_cell = agent.model.grid[current[0]][current[1]]
        if any(isinstance(a, GoalAgent) for a in AgentArquitecture_in_cell):
            agent.path_to_exit = path
            agent.has_explored = True
            return None

        if current not in self.visited:
            agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count
            self.step_count += 1
            self.visited.add(current)

            if diagonal:
                directions = [
                    (0, 1, False), (1, 1, True), (1, 0, False), (1, -1, True),
                    (0, -1, False), (-1, -1, True), (-1, 0, False), (-1, 1, True)
                ]
            else:
                directions = [(-1, 0, False), (0, 1, False), (1, 0, False), (0, -1, False)]

            for direction in directions:
                new_x, new_y, is_diagonal = current[0] + direction[0], current[1] + direction[1], direction[2]
                new_position = (new_x, new_y)

                if (
                    0 <= new_x < agent.model.grid.width
                    and 0 <= new_y < agent.model.grid.height
                    and new_position not in self.visited
                ):
                    AgentArquitecture_in_new_cell = agent.model.grid[new_x][new_y]
                    if all(isinstance(a, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for a in AgentArquitecture_in_new_cell):
                        new_cost = current_cost + (13 if is_diagonal else 10)
                        if new_position not in self.cost_so_far or new_cost < self.cost_so_far[new_position]:
                            self.cost_so_far[new_position] = new_cost
                            heapq.heappush(self.priority_queue, (new_cost, self.index, new_position, path + [new_position]))
                            self.index += 1

        return current
