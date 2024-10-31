from AgentArquitecture.bomberman import BombermanAgent
from mesa import Agent
import random

class GlobeAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        # Obtener una posición de destino aleatoria en una dirección válida
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