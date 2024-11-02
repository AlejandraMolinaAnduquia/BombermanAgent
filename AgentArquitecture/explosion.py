from mesa import Agent

class ExplosionAgent(Agent):
    def __init__(self, unique_id, model, position, duration=1):
        super().__init__(unique_id, model)
        self.position = position
        self.duration = duration  # Duración de la explosión en pasos de simulación

    def step(self):
        # Reduce la duración en cada paso y remueve el agente cuando se acabe el tiempo
        self.duration -= 1
        if self.duration <= 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
