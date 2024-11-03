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
            return  # Si no hay Bomberman, salir del método

        bomberman_position = bomberman.pos
        if bomberman_position is None:
            return  # Si la posición de Bomberman es None, salir del método

        if self.awaiting_step_confirmation:
            # Revisar colisión normal y colisión cruzada
            if self.check_collision(bomberman_position) or self.check_cross_collision(self.pos, bomberman):
                self.handle_collision(bomberman)
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

    def handle_collision(self, bomberman):
        """Detiene la simulación si ocurre una colisión entre GlobeAgent y Bomberman."""
        # Guarda la posición de la colisión
        collision_position = bomberman.pos

        # Elimina a Bomberman del modelo y detiene la simulación
        self.model.grid.remove_agent(bomberman)
        self.model.schedule.remove(bomberman)
        self.model.running = False  # Detiene la simulación

        # Imprime un mensaje con la posición de la colisión
        print(f"Colisión detectada entre GlobeAgent y BombermanAgent en la posición {collision_position}. Bomberman eliminado y simulación finalizada.")


    def get_bomberman_agent(self):
        for agent in self.model.schedule.agents:
            if isinstance(agent, BombermanAgent):
                return agent
        return None

    def check_collision(self, bomberman_position):
        x, y = self.pos
        bx, by = bomberman_position
        return abs(x - bx) + abs(y - by) == 0  # Cambia a 0 para la misma posición

    def check_cross_collision(self, current_position, bomberman):
        bx, by = bomberman.pos 
        next_bomberman_position = (bx + bomberman.direction[0], by + bomberman.direction[1])
        return current_position == next_bomberman_position