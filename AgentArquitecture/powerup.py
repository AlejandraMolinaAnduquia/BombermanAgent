from mesa import Agent
from AgentArquitecture.bomberman import BombermanAgent
from AgentArquitecture.road import RoadAgent

class PowerupAgent(Agent):
    def __init__(self, unique_id, model, original_visit_order=None):
        super().__init__(unique_id, model)
        self.original_visit_order = original_visit_order
        print(f"[Debug] PowerupAgent creado en la posición {self.pos} con orden de visita original {self.original_visit_order}")

    def step(self):
        # Verifica si el PowerupAgent sigue en la grilla antes de interactuar
        if self.pos is None:
            print("[Debug] PowerupAgent ya no está en la grilla.")
            return

        # Almacena la posición y el número de orden de visita antes de intentar cualquier operación de eliminación
        powerup_position = self.pos
        visit_order = self.original_visit_order
        
        # Comprueba si Bomberman está en la misma celda para recoger el Powerup
        agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])
        for agent in agents_in_cell:
            if isinstance(agent, BombermanAgent):
                # Incrementa el poder de destrucción de Bomberman
                agent.destruction_power += 1
                
                print(f"Comodín78 recogido en la posición: {powerup_position}. Poder de destrucción aumentado a {agent.destruction_power}.")

                # Elimina el PowerupAgent del modelo y de la grilla
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                
                print(f"[Debug] PowerupAgent eliminado de la posición {powerup_position}")

                # Crea el RoadAgent en la posición del Powerup con el número de orden original
                road = RoadAgent(self.model.next_id(), self.model)
                road.visit_order = visit_order if visit_order is not None else ""  # Asigna el número de orden si existe
                print(f"[Debug] Creando RoadAgent en la posición {powerup_position} con número de orden {road.visit_order}")

                # Coloca el RoadAgent en la posición y en el scheduler
                self.model.grid.place_agent(road, powerup_position)
                self.model.schedule.add(road)
                print(f"[Debug] RoadAgent con número de orden {road.visit_order} colocado en la posición {powerup_position} exitosamente")

                break  # Termina después de procesar el Powerup
