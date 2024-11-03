from AgentArquitecture.bomberman import BombermanAgent
from AgentArquitecture.road import RoadAgent
from mesa import Agent
import random

class GlobeAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.awaiting_step_confirmation = False  

    def step(self):
        bomberman = self.get_bomberman_agent()
        if bomberman is None:
            return  

        bomberman_position = bomberman.pos
        if self.awaiting_step_confirmation:
            if self.check_collision(bomberman_position) or self.check_cross_collision(self.pos, bomberman):
                self.model.running = False
                self.model.game_over_message = "Game Over"
                self.model.grid.remove_agent(bomberman)
                return 
            self.awaiting_step_confirmation = False

        if bomberman.is_moving:
            possible_directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(possible_directions)

            moved = False
            for direction in possible_directions:
                new_position = (self.pos[0] + direction[0], self.pos[1] + direction[1])

                if not self.model.grid.out_of_bounds(new_position) and self.model.is_cell_empty(new_position):
                    self.model.grid.place_agent(RoadAgent(self.model.next_id(), self.model), self.pos)
                    self.model.grid.move_agent(self, new_position)
                    self.awaiting_step_confirmation = True
                    moved = True
                    break

            if not moved:
                print("No se pudo mover el globo a ninguna nueva posición")


    def get_bomberman_agent(self):
        for agent in self.model.schedule.agents:
            if isinstance(agent, BombermanAgent):
                return agent
        return None

    def check_collision(self, bomberman_position):
        x, y = self.pos
        bx, by = bomberman_position
        print("posicion de BOMBERMAN COLISION: ", bx, by)
        return abs(x - bx) + abs(y - by) == 1

    def check_cross_collision(self, current_position, bomberman):
        bx, by = bomberman.pos 
        next_bomberman_position = (bx + bomberman.direction[0], by + bomberman.direction[1])
        return current_position == next_bomberman_position