from mesa import Agent

class BaseAgentLogic(Agent):
    def __init__(self, unique_id, model):
        """
        Inicializa el agente base con una posición inicial, poder de destrucción, y otros atributos.

        Args:
            unique_id: ID único del agente.
            model: Referencia al modelo al que pertenece el agente.
        """
        super().__init__(unique_id, model)
        self.pos = (0, 0)  # Posición inicial del agente.
        self.previous_pos = None  # Para almacenar la posición anterior si es necesario.
        self.destruction_power = 1  # Poder de destrucción del agente.
        self.waiting_for_explosion = False  # Indica si el agente espera una explosión activa.

    def move_to_position(self, next_position):
        """
        Mueve al agente a la posición especificada `next_position`.

        Args:
            next_position (tuple): La posición (x, y) a la que se moverá el agente.
        
        Prints:
            Muestra la posición actual del agente tras el movimiento, o un mensaje de error si
            `next_position` es inválida.
        """
        if next_position:
            self.model.grid.move_agent(self, next_position)
            print(f"Moviéndose a la posición: {self.pos}")
        else:
            print("Error: la siguiente posición es inválida.")

    def is_adjacent(self, pos1, pos2):
        """
        Determina si `pos2` está en una posición adyacente ortogonal a `pos1`.

        Args:
            pos1 (tuple): La posición (x, y) de referencia.
            pos2 (tuple): La posición (x, y) que se quiere verificar.
        
        Returns:
            bool: `True` si `pos2` está en una posición adyacente a `pos1`, `False` en caso contrario.
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1
