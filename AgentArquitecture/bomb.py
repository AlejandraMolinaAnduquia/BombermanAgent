from mesa import Agent
from random import random

class BombAgent(Agent):
    def __init__(self, unique_id, model, position, destruction_power):
        """
        Inicializa el agente de bomba con su posición, poder de destrucción y temporizador de explosión.

        Args:
            unique_id: Identificador único del agente.
            model: El modelo de simulación al que pertenece el agente.
            position: La posición inicial de la bomba en la cuadrícula.
            destruction_power: El poder de destrucción de la bomba, que define su radio de explosión.
        """
        super().__init__(unique_id, model)
        self.position = position  # Posición en la cuadrícula
        self.destruction_power = destruction_power  # Radio de destrucción de la bomba
        self.timer = destruction_power + 1  # Temporizador de explosión basado en el poder de destrucción
    
    def step(self):
        """
        Llama al paso de simulación del agente. Reduce el temporizador en cada paso
        y, cuando llega a cero, detona la bomba y la elimina de la simulación.
        """
        if self.timer > 0:
            self.timer -= 1  # Reduce el temporizador de la bomba
        else:
            self.explode()  # Detona la bomba cuando el temporizador llega a cero
            # Elimina la bomba de la grilla y el scheduler del modelo
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
    
    def explode(self):
        """
        Realiza la explosión de la bomba en su posición, afectando celdas cercanas según el poder de destrucción.
        Elimina rocas y globos, e interactúa con otros agentes en la cuadrícula, deteniendo la simulación si
        Bomberman es alcanzado.
        """
        from AgentArquitecture.rock import RockAgent
        from AgentArquitecture.powerup import PowerupAgent
        from AgentArquitecture.explosion import ExplosionAgent
        from AgentArquitecture.metal import MetalAgent
        from AgentArquitecture.bomberman import BombermanAgent
        from AgentArquitecture.globe import GlobeAgent
        from AgentArquitecture.goal import GoalAgent
        from AgentArquitecture.road import RoadAgent

        print(f"Explosión de bomba en: {self.position} con poder de destrucción: {self.destruction_power}")

        # Direcciones de expansión de la explosión (arriba, abajo, izquierda, derecha)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Explora cada dirección en el radio de explosión
        for direction in directions:
            for step in range(1, self.destruction_power + 1):
                # Calcula la posición objetivo en esta dirección y paso
                target_position = (self.position[0] + direction[0] * step, self.position[1] + direction[1] * step)
                
                if self.model.grid.out_of_bounds(target_position):
                    break  # Termina la expansión si sale de los límites de la cuadrícula

                # Obtiene agentes en la posición afectada
                agents_in_cell = self.model.grid.get_cell_list_contents([target_position])
                stop_explosion = False  # Controla la detención de la explosión en la dirección actual

                for agent in agents_in_cell:
                    # Si encuentra un MetalAgent, detiene la expansión en esta dirección
                    if isinstance(agent, MetalAgent):
                        stop_explosion = True
                        break
                    elif isinstance(agent, RockAgent):
                        # Guarda el número de orden de visita de la roca para transferirlo al PowerupAgent o RoadAgent
                        visit_order = getattr(agent, 'visit_order', None)

                        # Verificar si esta roca oculta la meta
                        if getattr(agent, 'has_exit', False):  # Se asume que 'RockAgent' tiene esta propiedad
                            # Elimina la roca y genera la meta
                            self.model.grid.remove_agent(agent)
                            self.model.schedule.remove(agent)

                            exit_agent = GoalAgent(self.model.next_id(), self.model)
                            self.model.grid.place_agent(exit_agent, target_position)
                            self.model.schedule.add(exit_agent)
                            print(f"Meta descubierta en la posición: {target_position}")
                        else:
                            # Elimina la roca de la cuadrícula y el modelo
                            self.model.grid.remove_agent(agent)
                            self.model.schedule.remove(agent)

                            if random() < 0.3:  # 30% de probabilidad de generar un Powerup en lugar de un camino
                                # Crea un PowerupAgent en la posición de la roca destruida con el número de orden de visita
                                powerup = PowerupAgent(self.model.next_id(), self.model, original_visit_order=visit_order)
                                self.model.grid.place_agent(powerup, target_position)
                                self.model.schedule.add(powerup)
                                print(f"Comodín generado en la posición: {target_position} con orden de visita {visit_order}")
                            else:
                                # Crea un camino (RoadAgent) en la posición de la roca destruida
                                road = RoadAgent(self.model.next_id(), self.model)
                                road.visit_order = visit_order  # Asigna el número de orden de visita
                                self.model.grid.place_agent(road, target_position)
                                self.model.schedule.add(road)
                                print(f"Camino creado en la posición: {target_position} con número de orden {visit_order}")

                        stop_explosion = True  # Detiene la explosión después de eliminar una roca

                    elif isinstance(agent, BombermanAgent):
                        # Si Bomberman es alcanzado, lo elimina y termina la simulación
                        self.model.grid.remove_agent(agent)
                        self.model.schedule.remove(agent)
                        self.model.running = False
                        print(f"Bomberman ha sido alcanzado por la explosión en {target_position} y ha muerto. Simulación finalizada.")
                        stop_explosion = True

                    elif isinstance(agent, GlobeAgent):
                        # Si un globo es alcanzado, lo elimina de la cuadrícula y el modelo
                        self.model.grid.remove_agent(agent)
                        self.model.schedule.remove(agent)
                        print(f"GlobeAgent destruido por la explosión en la posición {target_position}.")
                        stop_explosion = True

                if stop_explosion:
                    break  # Detiene la expansión de la explosión en esta dirección

                # Crea un agente de explosión en la posición afectada y lo coloca en el scheduler del modelo
                explosion = ExplosionAgent(self.model.next_id(), self.model, target_position, duration=1)
                self.model.grid.place_agent(explosion, target_position)
                self.model.schedule.add(explosion)