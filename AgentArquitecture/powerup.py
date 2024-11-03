from mesa import Agent
from AgentArquitecture.bomberman import BombermanAgent

class PowerupAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        # Verifica si el PowerupAgent sigue en la grilla antes de interactuar
        if self.pos is None:
            return  # Sale si el PowerupAgent ya fue recogido y removido
        
        # Comprueba si Bomberman está en la misma celda para recoger el comodín
        agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])
        for agent in agents_in_cell:
            if isinstance(agent, BombermanAgent):
                agent.destruction_power += 1  # Incrementa el poder de destrucción
                # Elimina el comodín del modelo y de la grilla
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                print(f"Comodín recogido en la posición: {self.pos}. Poder de destrucción aumentado a {agent.destruction_power}.")
                break
