from mesa import Agent

class BaseAgentLogic(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.pos = (0, 0)  # Posición inicial común
        self.previous_pos = None
        self.destruction_power = 1  # Poder inicial de destrucción
        self.waiting_for_explosion = False  # Indicador de si hay una bomba activa

    def move_to_position(self, next_position):
        """Mueve al agente a la posición siguiente."""
        if next_position:
            self.model.grid.move_agent(self, next_position)
            print(f"Moviéndose a la posición: {self.pos}")
        else:
            print("Error: la siguiente posición es inválida.")

    def is_adjacent(self, pos1, pos2):
        """Verifica si `pos2` está en una casilla adyacente ortogonal a `pos1`."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1
