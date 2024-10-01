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
        self.posicion_actual = None  # Posición actual de Bomberman

    def mover(self):
        # Obtener las celdas adyacentes que son "C" (caminos)
        vecinos = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False)
        caminos = []
        for vecino in vecinos:
            if isinstance(vecino, tuple):
                if self.model.grid.is_cell_empty(vecino) or 'C' in self.model.grid.get_cell_list_contents(vecino):
                    caminos.append(vecino)
            else:
                pos = vecino.pos
                if self.model.grid.is_cell_empty(pos) or 'C' in self.model.grid.get_cell_list_contents(pos):
                    caminos.append(pos)

        if caminos:
            nueva_posicion = random.choice(caminos)
            self.model.grid.move_agent(self, nueva_posicion)
            self.posicion_actual = nueva_posicion

    def colocar_bomba(self):
        # Coloca una bomba en la posición actual de Bomberman
        if self.posicion_actual:
            bomba = {"pos": self.posicion_actual, "timer": self.poder_destruccion + 2}
            self.bombas.append(bomba)
            print(f"Bomba colocada en {self.posicion_actual} con timer {self.poder_destruccion + 2}")

    def explotar_bomba(self):
        # Explosión de bombas. Solo destruyen rocas "R" en el radio de poder_destruccion
        for bomba in self.bombas[:]:  # Usamos una copia para iterar
            bomba["timer"] -= 1
            if bomba["timer"] <= 0:
                # Buscar celdas en el rango de poder de destrucción
                rango = self.poder_destruccion
                for dx in range(-rango, rango + 1):
                    for dy in range(-rango, rango + 1):
                        pos_explosion = (bomba["pos"][0] + dx, bomba["pos"][1] + dy)
                        # Si es una roca "R", se destruye
                        if self.model.grid.out_of_bounds(pos_explosion):
                            continue
                        contenido = self.model.grid.get_cell_list_contents(pos_explosion)
                        if 'R' in contenido:
                            self.model.grid.remove_agent(pos_explosion)
                            print(f"Roca destruida en {pos_explosion}")
                # Eliminar la bomba del mapa
                self.bombas.remove(bomba)

    def step(self):
        # Acción que realiza el agente en cada paso de la simulación
        self.mover()  # Mover Bomberman
        if random.random() < 0.1:  # Probabilidad de colocar una bomba
            self.colocar_bomba()
        self.explotar_bomba()  # Verificar explosiones de bombas
