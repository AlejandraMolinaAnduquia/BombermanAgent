from mesa import Agent
from random import random

class BombAgent(Agent):
    def __init__(self, unique_id, model, position, destruction_power):
        super().__init__(unique_id, model)
        self.position = position
        self.destruction_power = destruction_power
        self.timer = destruction_power + 1 
    
    def step(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.explode()
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
    
    def explode(self):
        from AgentArquitecture.rock import RockAgent
        from AgentArquitecture.powerup import PowerupAgent
        from AgentArquitecture.explosion import ExplosionAgent
        from AgentArquitecture.metal import MetalAgent
        from AgentArquitecture.bomberman import BombermanAgent
        from AgentArquitecture.globe import GlobeAgent
        from AgentArquitecture.road import RoadAgent

        print(f"Explosión de bomba en: {self.position} con poder de destrucción: {self.destruction_power}")

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for direction in directions:
            for step in range(1, self.destruction_power + 1):
                target_position = (self.position[0] + direction[0] * step, self.position[1] + direction[1] * step)
                
                if self.model.grid.out_of_bounds(target_position):
                    break

                agents_in_cell = self.model.grid.get_cell_list_contents([target_position])
                stop_explosion = False

                for agent in agents_in_cell:
                    if isinstance(agent, MetalAgent):
                        stop_explosion = True
                        break
                    elif isinstance(agent, RockAgent):
                        # Guarda el número de orden de visita de la roca para el PowerupAgent o RoadAgent
                        visit_order = getattr(agent, 'visit_order', None)

                        # Remueve la roca y crea un Powerup o un camino en su lugar
                        self.model.grid.remove_agent(agent)
                        self.model.schedule.remove(agent)

                        if random() < 0.3:
                            # Crear el PowerupAgent con el visit_order de la roca
                            powerup = PowerupAgent(self.model.next_id(), self.model, original_visit_order=visit_order)
                            self.model.grid.place_agent(powerup, target_position)  
                            self.model.schedule.add(powerup)
                            print(f"Comodín generado en la posición: {target_position} con orden de visita {visit_order}")
                        else:
                            # Crear un camino en la posición de la roca destruida y asignarle el orden de visita
                            road = RoadAgent(self.model.next_id(), self.model)
                            road.visit_order = visit_order
                            self.model.grid.place_agent(road, target_position)
                            self.model.schedule.add(road)
                            print(f"Camino creado en la posición: {target_position} con número de orden {visit_order}")

                        stop_explosion = True

                    elif isinstance(agent, BombermanAgent):
                        self.model.grid.remove_agent(agent)
                        self.model.schedule.remove(agent)
                        self.model.running = False
                        print(f"Bomberman ha sido alcanzado por la explosión en {target_position} y ha muerto. Simulación finalizada.")
                        stop_explosion = True

                    elif isinstance(agent, GlobeAgent):
                        self.model.grid.remove_agent(agent)
                        self.model.schedule.remove(agent)
                        print(f"GlobeAgent destruido por la explosión en la posición {target_position}.")
                        stop_explosion = True

                if stop_explosion:
                    break

                # Coloca un agente de explosión en la posición afectada
                explosion = ExplosionAgent(self.model.next_id(), self.model, target_position, duration=1)
                self.model.grid.place_agent(explosion, target_position)
                self.model.schedule.add(explosion)

