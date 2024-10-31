from AgentArquitecture.bomberman import BombermanAgent
from mesa import Agent
import random

class GlobeAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        bomberman = self.get_bomberman_agent()  # Implementa este método para obtener el agente Bomberman

        # Solo permitir que el globo se mueva si Bomberman ha comenzado a moverse
        if bomberman.is_moving: 
            possible_directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(possible_directions)
            
            for direction in possible_directions:
                new_position = (self.pos[0] + direction[0], self.pos[1] + direction[1])

                # Verificar si la nueva posición está dentro de los límites y está vacía
                if self.model.grid.out_of_bounds(new_position):
                    continue
                if self.model.is_cell_empty(new_position):
                    # Mover el agente a la nueva posición si está vacía
                    self.model.grid.move_agent(self, new_position)
                    break
    
    def get_bomberman_agent(self):
        for agent in self.model.schedule.agents:
            if isinstance(agent, BombermanAgent):
                return agent
        return None