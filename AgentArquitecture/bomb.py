from mesa import Agent
import random
from AgentArquitecture.explosion import ExplosionAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.metal import MetalAgent
from AgentArquitecture.bomberman import BombermanAgent

class BombAgent(Agent):
    def __init__(self, unique_id, model, position, destruction_power):
        super().__init__(unique_id, model)
        self.position = position
        self.destruction_power = destruction_power
        self.timer = destruction_power + 2  # El tiempo de detonación es pd + 2 segundos
    
    def step(self):
        # Reduce el temporizador en cada paso
        if self.timer > 0:
            self.timer -= 1
        else:
            # Detonar la bomba
            self.explode()
            # Remover la bomba después de explotar
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
    
    def explode(self):
        # Define las direcciones ortogonales
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for direction in directions:
            for step in range(1, self.destruction_power + 1):
                target_position = (self.position[0] + direction[0] * step, self.position[1] + direction[1] * step)
                
                # Verifica si está dentro de los límites
                if self.model.grid.out_of_bounds(target_position):
                    break
                
                # Revisa si hay agentes en la posición objetivo
                agents_in_cell = self.model.grid.get_cell_list_contents([target_position])
                stop_explosion = False
                
                for agent in agents_in_cell:
                    if isinstance(agent, RockAgent):
                        # Destruye la roca y coloca una explosión
                        self.model.grid.remove_agent(agent)
                        self.model.schedule.remove(agent)
                        stop_explosion = True
                    elif isinstance(agent, MetalAgent):
                        # La explosión no puede pasar a través del metal
                        stop_explosion = True
                    elif isinstance(agent, BombermanAgent):
                        # Si Bomberman está en la posición, termina la simulación
                        self.model.running = False
                        stop_explosion = True

                # Crear el agente de explosión
                explosion = ExplosionAgent(self.model.next_id(), self.model, target_position, duration=1)
                self.model.grid.place_agent(explosion, target_position)
                self.model.schedule.add(explosion)

                # Detener la expansión de la explosión si golpea algo
                if stop_explosion:
                    break
