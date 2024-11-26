from mesa import Agent

class GoalAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.visit_order = None  # Indica el orden de visita si es relevante para la lógica del juego
        self.is_visited = False  # Marca si Bomberman alcanzó la meta

    def step(self):
        """
        Este método puede usarse para realizar verificaciones o actualizaciones, 
        como marcar si la meta fue alcanzada.
        """
        if self.is_visited:
            print(f"Meta alcanzada en la posición {self.pos} por Bomberman.")
            self.model.running = False  # Detener el modelo si la meta es alcanzada
