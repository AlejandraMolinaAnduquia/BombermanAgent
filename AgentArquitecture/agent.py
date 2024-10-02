from collections import deque
from .model import *
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
        self.ruta_hacia_salida = None  # Para almacenar la ruta calculada por BFS

    def bfs_move(self):
        start_pos = self.pos  # Posición actual de Bomberman
        goal_pos = self.model.find_exit()  # Método que busca la salida en el modelo
        
        if not goal_pos:
            print("Salida no encontrada en el mapa.")
            return
        
        # Cola para BFS
        cola = deque([start_pos])
        # Conjunto de posiciones visitadas
        visitados = {start_pos}
        # Diccionario para rastrear el camino
        caminos = {start_pos: None}
        
        while cola:
            actual = cola.popleft()
            
            # Si encontramos la salida, reconstruimos el camino
            if actual == goal_pos:
                self.ruta_hacia_salida = []
                while actual:
                    self.ruta_hacia_salida.insert(0, actual)
                    actual = caminos[actual]
                return  # Salimos del método, ruta está lista

            # Vecinos de la posición actual
            vecinos = self.model.grid.get_neighborhood(actual, moore=False, include_center=False)
            for vecino in vecinos:
                if vecino not in visitados and (self.model.grid.is_cell_empty(vecino) or
                                                isinstance(self.model.grid.get_cell_list_contents([vecino])[0], Comodin)):
                    visitados.add(vecino)
                    cola.append(vecino)
                    caminos[vecino] = actual  # Mantener el camino para retroceder desde la salida

        print("No se encontró la salida en la búsqueda BFS.")

    def step(self):
        # Si ya tiene una ruta calculada, seguirla
        if self.ruta_hacia_salida:
            next_move = self.ruta_hacia_salida.pop(0)
            self.model.grid.move_agent(self, next_move)
            print(f"Bomberman se movió a {next_move}")
        else:
            # Realizar BFS para calcular la ruta
            self.bfs_move()
    
    def step(self):
        self.mover()
        if random.random() < 0.1:
            self.colocar_bomba()
        self.recoger_comodin()
    

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
            # Verificar si la celda actual contiene un comodín
            celda_actual = self.model.grid.get_cell_list_contents([self.pos])
            if any(isinstance(obj, Comodin) for obj in celda_actual):
                print(f"No se puede colocar bomba en {self.pos} porque hay un comodín.")
                return  # No colocar la bomba si hay un comodín en la celda

            # Si no hay comodín, se puede colocar la bomba
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

class Explosion(Agent):
    def __init__(self, pos, model, duration):
        super().__init__(pos, model)
        self.pos = pos
        self.duration = duration  # Tiempo que la explosión será visible

    def step(self):
        self.duration -= 1
        if self.duration <= 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            
class Bomba(Agent):
    def __init__(self, pos, model, poder_destruccion, bomberman):
        super().__init__(pos, model)
        self.pos = pos
        self.timer = poder_destruccion + 2  # Temporizador de la bomba
        self.poder_destruccion = poder_destruccion
        self.bomberman = bomberman  # Referencia al Bomberman que colocó la bomba

    def step(self):
        self.timer -= 1
        print(f"Temporizador de bomba en {self.timer}")  # Añade esto para verificar
        if self.timer <= 0:
            print(f"Bomba explotó en {self.pos}")
            self.explotar()
            self.model.grid.remove_agent(self)  # Eliminar la bomba del grid
            self.model.schedule.remove(self)  # Eliminar la bomba del schedule
            self.bomberman.bomba_activa = False  # Permitir que el Bomberman coloque otra bomba

    def explotar(self):
        if self.pos is not None:
            x, y = self.pos  # Obtener la posición de la bomba
            # Lógica para destruir rocas en las direcciones cardinales
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:  # Explosión en las 4 direcciones
                for alcance in range(1, self.poder_destruccion + 1):
                    vecino_x, vecino_y = x + dx * alcance, y + dy * alcance
                    if self.model.grid.out_of_bounds((vecino_x, vecino_y)):
                        break  # Salir si la celda está fuera de los límites
                    vecinos = self.model.grid.get_cell_list_contents((vecino_x, vecino_y))

                    # Detener la explosión si se encuentra con metal
                    if any(isinstance(obj, Metal) for obj in vecinos):
                        break

                    # Si hay un comodín, la explosión sigue sin afectarlo
                    if any(isinstance(obj, Comodin) for obj in vecinos):
                        print(f"Explosión ignoró el comodín en ({vecino_x}, {vecino_y})")
                        continue  # La explosión continúa su camino sin afectar el comodín

                    # Destruir rocas o rocas con salida
                    for obj in vecinos:
                        if isinstance(obj, Roca) or isinstance(obj, RocaSalida):
                            print(f"Roca destruida en ({vecino_x}, {vecino_y})")
                            self.model.grid.remove_agent(obj)  # Eliminar la roca del grid
                            
                            # Colocar un comodín si hay disponibles
                            if self.model.comodines_colocados < self.model.num_comodines:
                                comodin = Comodin((vecino_x, vecino_y), self.model)
                                self.model.grid.place_agent(comodin, (vecino_x, vecino_y))
                                self.model.schedule.add(comodin)
                                self.model.comodines_colocados += 1
                                print(f"Comodín colocado en ({vecino_x}, {vecino_y})")
                            break  # Detener la explosión en esta dirección después de destruir la roca
                    
                    # Si no se destruye una roca ni hay metal, la explosión sigue en esa dirección
                    else:
                        print(f"Explosión alcanzó ({vecino_x}, {vecino_y})")
                        explosion = Explosion((vecino_x, vecino_y), self.model, duration=1)  # Pintar por 1 paso
                        self.model.grid.place_agent(explosion, (vecino_x, vecino_y))
                        self.model.schedule.add(explosion)
                        continue  # Continuar con el siguiente alcance en la misma dirección

                    break  # Detenerse al encontrar una roca o metal en la dirección actual


            


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
