from mesa import Agent

class RockAgent(Agent):
    def __init__(self, unique_id, model, has_exit=False):
        """
        Inicializa la roca con un indicador opcional de que contiene la salida.
        Args:
            unique_id: Identificador único.
            model: El modelo al que pertenece.
            has_exit: Indica si esta roca oculta la salida (R_s).
        """
        super().__init__(unique_id, model)
        self.has_exit = has_exit
        self.is_visited = False
        self.visit_order = None
