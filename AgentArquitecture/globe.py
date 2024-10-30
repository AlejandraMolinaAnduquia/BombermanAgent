from AgentArquitecture.bomberman import BombermanAgent
from mesa import Agent
import random

class GlobeAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        valid_moves = [pos for pos in neighbors if self.model.grid.is_cell_empty(pos)]
        
        if valid_moves:
            next_position = random.choice(valid_moves)
            self.model.grid.move_agent(self, next_position)

        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for agent in cell_contents:
            if isinstance(agent, BombermanAgent):
                self.model.game_over = True #modificar accion
                break