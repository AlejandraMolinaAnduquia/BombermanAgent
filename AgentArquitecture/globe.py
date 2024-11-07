from AgentArquitecture.bomberman import BombermanAgent
from AgentArquitecture.road import RoadAgent
from mesa import Agent
import random

class GlobeAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.awaiting_step_confirmation = False
        self.previous_visit_order = None  # Almacena el número de orden de la casilla de camino
        self.visit_order = None
        self.is_visited = False

    def step(self):
        if self.pos is None:
            return

        bomberman = self.get_bomberman_agent()
        if bomberman is None or bomberman.pos is None:
            return

        if self.awaiting_step_confirmation:
            if self.check_collision(bomberman.pos) or self.check_cross_collision(self.pos, bomberman):
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
                    # Crear un camino en la posición actual del globo antes de moverse
                    current_cell_agents = self.model.grid.get_cell_list_contents([self.pos])
                    for agent in current_cell_agents:
                        if isinstance(agent, RoadAgent):
                            # Guarda el número de visita si la casilla actual es un camino numerado
                            self.previous_visit_order = agent.visit_order

                    # Colocar un camino en la posición actual del globo antes de moverse
                    road = RoadAgent(self.model.next_id(), self.model)
                    road.visit_order = self.previous_visit_order  # Mantiene el número de orden si lo tenía
                    self.model.grid.place_agent(road, self.pos)

                    # Mueve el globo a la nueva posición
                    self.model.grid.move_agent(self, new_position)
                    self.awaiting_step_confirmation = True
                    moved = True
                    break

            if not moved:
                print("No se pudo mover el globo a ninguna nueva posición")

    def handle_collision(self, bomberman):
        collision_position = bomberman.pos
        self.model.grid.remove_agent(bomberman)
        self.model.schedule.remove(bomberman)
        self.model.running = False
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
