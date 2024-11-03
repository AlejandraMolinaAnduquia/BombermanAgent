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
        from AgentArquitecture.globe import GlobeAgent  # Asegúrate de importar GlobeAgent

        print(f"Explosión de bomba en: {self.position} con poder de destrucción: {self.destruction_power}")

        affected_positions = [self.position]
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
                        stop_explosion = True  # Detener la expansión si encuentra metal
                        break
                    elif isinstance(agent, RockAgent):
                        self.model.grid.remove_agent(agent)
                        self.model.schedule.remove(agent)
                        stop_explosion = True
                        
                        # Probabilidad de generar un comodín en la posición de la roca destruida
                        if random() < 0.3:  # 30% de probabilidad
                            powerup = PowerupAgent(self.model.next_id(), self.model)
                            self.model.grid.place_agent(powerup, target_position)
                            self.model.schedule.add(powerup)
                            print(f"Comodín generado en la posición: {target_position}")

                    elif isinstance(agent, BombermanAgent):
                        self.model.grid.remove_agent(agent)
                        self.model.schedule.remove(agent)
                        self.model.running = False  # Detener la simulación
                        print(f"Bomberman ha sido alcanzado por la explosión en {target_position} y ha muerto. Simulación finalizada.")
                        stop_explosion = True

                    elif isinstance(agent, GlobeAgent):
                        self.model.grid.remove_agent(agent)
                        self.model.schedule.remove(agent)
                        print(f"GlobeAgent destruido por la explosión en la posición {target_position}.")  # Mensaje de eliminación del globo

                if stop_explosion:
                    break  # Si el metal u otro obstáculo detiene la explosión, no continúa expandiéndose

                affected_positions.append(target_position)
                
                # Coloca un agente de explosión en la posición afectada
                explosion = ExplosionAgent(self.model.next_id(), self.model, target_position, duration=1)
                self.model.grid.place_agent(explosion, target_position)
                self.model.schedule.add(explosion)

        print(f"Área afectada por la explosión en el step actual: {affected_positions}")


