import os
import sys

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mesa import Agent
import random

class Comodin(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos

    def step(self):
        pass  # El comodín no hace nada en cada paso


class Bomberman(Agent):
    def __init__(self, unique_id, model, poder_destruccion):
        super().__init__(unique_id, model)
        self.poder_destruccion = poder_destruccion
        self.bomba_activa = False

    def mover(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        # Filtrar las celdas vacías y las celdas de comodines
        empty_cells = [cell for cell in possible_steps if self.model.grid.is_cell_empty(cell) or 
                    isinstance(self.model.grid.get_cell_list_contents([cell])[0], Comodin)]
        
        if len(empty_cells) > 0:
            new_position = self.random.choice(empty_cells)
            self.model.grid.move_agent(self, new_position)
            print(f"Bomberman se movió a {self.pos}")


    def colocar_bomba(self):
        if not self.bomba_activa:
            bomba = Bomba(self.pos, self.model, self.poder_destruccion, self)
            self.model.grid.place_agent(bomba, self.pos)
            self.model.schedule.add(bomba)
            self.bomba_activa = True
            print(f"Bomba colocada en {self.pos} con timer {bomba.timer}")
        else:
            print("No se puede colocar otra bomba hasta que la actual explote.")

    def recoger_comodin(self):
        # Verificar solo la celda actual del Bomberman
        celda_actual = self.model.grid.get_cell_list_contents([self.pos])
        for obj in celda_actual:
            if isinstance(obj, Comodin):  # Verifica si hay un comodín en la celda actual
                self.poder_destruccion += 1
                self.model.grid.remove_agent(obj)  # Elimina el comodín una vez recogido
                self.model.schedule.remove(obj)  # Elimina el comodín del schedule
                print(f"Bomberman ha recogido un comodín. Poder de destrucción incrementado a {self.poder_destruccion}.")
                break

            
    def step(self):
        self.mover()
        if random.random() < 0.1:
            self.colocar_bomba()
        self.recoger_comodin()


class Bomba(Agent):
    def __init__(self, pos, model, poder_destruccion, bomberman):
        super().__init__(pos, model)
        self.pos = pos
        self.timer = poder_destruccion + 2  # Temporizador de la bomba
        self.poder_destruccion = poder_destruccion
        self.bomberman = bomberman  # Referencia al Bomberman que colocó la bomba

    def step(self):
        self.timer -= 1
        if self.timer <= 0:
            print(f"Bomba explotó en {self.pos}")
            self.explotar()
            self.model.grid.remove_agent(self)  # Eliminar la bomba del grid
            self.model.schedule.remove(self)  # Eliminar la bomba del schedule
            self.bomberman.bomba_activa = False  # Permitir que el Bomberman coloque otra bomba

# Modifica el método explotar en la clase Bomba
    def explotar(self):
        if self.pos is not None:
            x, y = self.pos  # Asignar la posición actual de la bomba
            # Lógica para destruir rocas en las direcciones cardinales
            for dx, dy in [(self.poder_destruccion, 0), (-self.poder_destruccion, 0), (0, self.poder_destruccion), (0, -self.poder_destruccion)]:
                vecino_x, vecino_y = x + dx, y + dy
                if self.model.grid.out_of_bounds((vecino_x, vecino_y)):
                    continue
                vecino = self.model.grid.get_cell_list_contents([(vecino_x, vecino_y)])
                for obj in vecino:
                    if isinstance(obj, Roca):
                        self.model.grid.remove_agent(obj)
                        print(f"Roca destruida en ({vecino_x}, {vecino_y})")
                        # Colocar un comodín en la posición de la roca destruida
                        comodin = Comodin((vecino_x, vecino_y), self.model)
                        self.model.grid.place_agent(comodin, (vecino_x, vecino_y))
                        self.model.schedule.add(comodin)  # Añadir el comodín al schedule
                        print(f"Comodín colocado en ({vecino_x}, {vecino_y})")
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