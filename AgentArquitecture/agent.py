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
        self.bombas = []  # Lista de bombas colocadas

    def mover(self):
        # Obtener las celdas adyacentes que son vacías
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        empty_cells = [cell for cell in possible_steps if self.model.grid.is_cell_empty(cell)]
        
        # Mover a una celda vacía si hay alguna disponible
        if len(empty_cells) > 0:
            new_position = self.random.choice(empty_cells)
            self.model.grid.move_agent(self, new_position)

    def colocar_bomba(self):
        # Coloca una bomba en la posición actual de Bomberman
        bomba = {"pos": self.pos, "timer": 3}  # Temporizador de la bomba
        self.bombas.append(bomba)
        print(f"Bomba colocada en {self.pos} con timer 3")

    def manejar_bombas(self):
        # Reducir el temporizador de las bombas y explotar si llega a 0
        bombas_a_explotar = []
        for bomba in self.bombas:
            bomba["timer"] -= 1
            if bomba["timer"] <= 0:
                bombas_a_explotar.append(bomba)

        # Eliminar las bombas que explotan y realizar la explosión
        for bomba in bombas_a_explotar:
            print(f"Bomba explotó en {bomba['pos']}")
            self.bombas.remove(bomba)
            self.explotar_bomba(bomba['pos'])

    def explotar_bomba(self, pos):
        # Simular la explosión de la bomba destruyendo rocas cercanas
        neighboring_cells = self.model.grid.get_neighborhood(pos, moore=True, include_center=True)
        for neighbor in neighboring_cells:
            contents = self.model.grid.get_cell_list_contents(neighbor)
            for obj in contents:
                if isinstance(obj, Roca):
                    print(f"Roca destruida en {neighbor}")
                    self.model.grid.remove_agent(obj)  # Eliminar la roca destruida

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
        self.manejar_bombas()  # Manejar bombas y explosiones
        self.recoger_comodin()  # Verificar si se ha recogido un comodín


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
