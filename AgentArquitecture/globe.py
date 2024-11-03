from AgentArquitecture.bomberman import BombermanAgent
from AgentArquitecture.road import RoadAgent
from mesa import Agent
import random

class GlobeAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.awaiting_step_confirmation = False  # Nuevo estado para confirmar el paso de ambos

    def step(self):
        # Obtener el agente Bomberman para verificar su estado y posición
        bomberman = self.get_bomberman_agent()
        if bomberman is None:
            return  # Si no encuentra a Bomberman, termina el paso actual

        bomberman_position = bomberman.pos

        # Verificar colisión si estamos en modo de espera
        if self.awaiting_step_confirmation:
            if self.check_collision(bomberman_position) or self.check_cross_collision(self.pos, bomberman):
                # Confirmar la colisión y detener el juego
                self.model.running = False
                self.model.game_over_message = "Game Over"

                # Eliminar a Bomberman del grid
                self.model.grid.remove_agent(bomberman)

                return  # Terminar el paso del globo tras la eliminación de Bomberman

            # Si no hubo colisión, desactivar el modo de espera
            self.awaiting_step_confirmation = False

        # Mover el globo si Bomberman está en movimiento
        if bomberman.is_moving:
            possible_directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(possible_directions)

            moved = False
            for direction in possible_directions:
                new_position = (self.pos[0] + direction[0], self.pos[1] + direction[1])

                # Verificar si la nueva posición está dentro de los límites y está vacía
                if not self.model.grid.out_of_bounds(new_position) and self.model.is_cell_empty(new_position):
                    # Convertir la posición actual del globo en un camino
                    self.model.grid.place_agent(RoadAgent(self.model.next_id(), self.model), self.pos)

                    # Mover el globo a la nueva posición
                    self.model.grid.move_agent(self, new_position)

                    # Activar modo de espera para la siguiente confirmación de paso
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
        # Verificar si el globo y Bomberman están en posiciones adyacentes
        x, y = self.pos
        bx, by = bomberman_position
        print("posicion de BOMBERMAN COLISION: ", bx, by)
        return abs(x - bx) + abs(y - by) == 1

    def check_cross_collision(self, new_position, bomberman):
        # Verificar colisión cruzada: si están a dos posiciones de distancia y se dirigen a la misma posición
        bx, by = bomberman.pos
        next_bomberman_position = (bx + bomberman.direction[0], by + bomberman.direction[1])

        # Comparar las posiciones futuras de Bomberman y del globo
        return new_position == next_bomberman_position