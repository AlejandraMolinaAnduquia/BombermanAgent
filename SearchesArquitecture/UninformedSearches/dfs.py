from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent

class dfs(SearchStrategy):
    def __init__(self):
        self.stack = []
        self.visited = set()
        self.step_count = 0

    def start_search(self, start):
        self.stack.append(start)

    def explore_step(self, agent, diagonal = False):
        if not self.stack:
            return None
        
        current, path = self.stack.pop()

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
                    (0, 1), (1, 1), (1, 0), (1, -1),
                    (0, -1), (-1, -1), (-1, 0), (-1, 1)
                ]
            else:
                #direcciones = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

            directions.reverse()
            for direction in directions:
                new_x, new_y = current[0] + direction[0], current[1] + direction[1]
                new_position = (new_x, new_y)

                if (
                    0 <= new_x < agent.model.grid.width
                    and 0 <= new_y < agent.model.grid.height
                    and new_position not in self.visited
                ):
                    AgentArquitecture_in_new_cell = agent.model.grid[new_x][new_y]
                    if all(isinstance(a, (RoadAgent, GoalAgent)) for a in AgentArquitecture_in_new_cell):
                        self.stack.append((new_position, path + [new_position]))

        return current