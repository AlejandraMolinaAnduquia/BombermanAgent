import os
import sys

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mesa import Agent
import random

class Bomberman(Agent):
    def __init__(self, unique_id, model, poder_destruccion):
        super().__init__(unique_id, model)
        self.poder_destruccion = poder_destruccion  # Poder de destrucción inicial

    def mover(self):
        # Obtener las celdas adyacentes que son vacías
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        empty_cells = [cell for cell in possible_steps if self.model.grid.is_cell_empty(cell)]
        
        # Mover a una celda vacía si hay alguna disponible
        if len(empty_cells) > 0:
            new_position = self.random.choice(empty_cells)
            self.model.grid.move_agent(self, new_position)
            print(f"Bomberman se movió a {self.pos}")

    def colocar_bomba(self):
        # Coloca una bomba en la posición actual de Bomberman
        bomba = Bomba(self.pos, self.model, self.poder_destruccion)
        self.model.grid.place_agent(bomba, self.pos)
        self.model.schedule.add(bomba)
        print(f"Bomba colocada en {self.pos} con timer {bomba.timer}")

    def recoger_comodin(self):
        # Si Bomberman destruye una roca con un comodín debajo, aumenta su poder de destrucción
        vecinos = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        for vecino in vecinos:
            if isinstance(vecino, RocaSalida):  # Asumiendo que el comodín está debajo de una RocaSalida
                self.poder_destruccion += 1
                print(f"Bomberman ha recogido un comodín. Poder de destrucción incrementado a {self.poder_destruccion}.")

    def step(self):
        # Acción que realiza el agente en cada paso de la simulación
        self.mover()  # Mover Bomberman
        if random.random() < 0.1:  # Probabilidad de colocar una bomba
            self.colocar_bomba()
        self.recoger_comodin()  # Verificar si se ha recogido un comodín
        #print(f"Bomberman está en {self.pos}")  # Mostrar la posición actual del Bomberman


class Bomba(Agent):
    def __init__(self, pos, model, poder_destruccion):
        super().__init__(pos, model)
        self.pos = pos
        self.timer = poder_destruccion + 2  # Temporizador de la bomba
        self.poder_destruccion = poder_destruccion

    def step(self):
        # Reducir el temporizador de la bomba
        self.timer -= 1
        if self.timer <= 0:
            print(f"Bomba explotó en {self.pos}")
            self.explotar()
            self.model.grid.remove_agent(self)  # Eliminar la bomba del grid
            self.model.schedule.remove(self)  # Eliminar la bomba del schedule

    def explotar(self):
        if self.pos is not None:
            x, y = self.pos  # Asignar la posición actual de la bomba
            
            # Lógica para destruir rocas en las direcciones cardinales
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                vecino_x, vecino_y = x + dx, y + dy
                # Destruir roca si es válida
                if self.model.grid.out_of_bounds((vecino_x, vecino_y)):
                    continue
                vecino = self.model.grid.get_cell_list_contents([(vecino_x, vecino_y)])
                for obj in vecino:
                    if isinstance(obj, Roca):
                        self.model.grid.remove_agent(obj)
                        print(f"Roca destruida en ({vecino_x}, {vecino_y})")
        else:
            print("Error: La bomba no tiene una posición válida.")


class Roca(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos

    def step(self):
        pass  # Las rocas no hacen nada en cada paso

class RocaSalida(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos

    def step(self):
        pass  # Similar a Roca, pero esta indica que tiene la salida

class Metal(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos

    def step(self):
        pass  # El metal tampoco hace nada, solo es indestructible
