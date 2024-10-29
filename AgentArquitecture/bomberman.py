from mesa import Agent
from AgentArquitecture.road import RoadAgent

class BombermanAgent(Agent):
    def __init__(self, unique_id, model, search_trategy):
        super().__init__(unique_id, model)
        self.search_strategy = search_trategy
        self.path_to_exit = []
        self.has_explored = False
        self.is_search_initialized = False

    def move_to_exit(self):
        if self.path_to_exit:
            next_position = self.path_to_exit.pop(0)
            self.model.grid.move_agent(self, next_position)

    def step(self):
        self.visit_cell()
        if not self.is_search_initialized:
            start_position = (self.pos[0], self.pos[1])
            self.search_strategy.start_search((start_position, [start_position]))
            self.is_search_initialized = True
        
        if not self.has_explored:
            self.search_strategy.explore_step(self)
        else:
            if self.path_to_exit:
                next_pos = self.path_to_exit.pop(0)
                self.model.grid.move_agent(self, next_pos)

    def visit_cell(self):
        AgentArquitecture_in_position = self.model.grid.get_cell_list_contents([self.pos])
        for agent in AgentArquitecture_in_position:
            if isinstance(agent, RoadAgent):
                agent.is_visited = True
                break