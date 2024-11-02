from mesa import Agent
from AgentArquitecture.bomberman import BombermanAgent


class PowerupAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        # Comprueba si Bomberman está en la misma celda para recoger el comodín
        agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])
        for agent in agents_in_cell:
            if isinstance(agent, BombermanAgent):
                agent.destruction_power += 1  # Incrementa el poder de destrucción
                # Elimina el comodín del modelo y de la grilla
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                break
