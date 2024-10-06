from collections import deque
from model import *
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
        self.stack = []  # Pila para backtracking (camino)
        self.visited = set()  # Conjunto de celdas visitadas
        self.objetivo_encontrado = False  # Variable para indicar si Bomberman ya ha encontrado la salida
       
    def dfs_step(self):
        # Si la salida ya fue encontrada, no continuar
        if self.objetivo_encontrado:
            return

        # Si la posición inicial es None, intentar obtener la posición actual del agente desde la grilla
        if self.pos is None:
            print("La posición actual es None, tratando de obtener la posición desde la grilla.")
            self.pos = self.model.grid.find_empty()
        
        # Si no hay más movimientos en la pila, terminamos la búsqueda
        if not self.stack:
            # Añadir la posición inicial de Bomberman al stack solo si está definida
            if self.pos is not None:
                self.stack.append(self.pos)
                self.visited.add(self.pos)
            else:
                print("Posición actual es None.")
                return

        current_pos = self.stack[-1]  # Tomar la posición actual (último elemento en la pila)

        # Verificar si la posición está dentro de los límites antes de intentar acceder a la celda
        if self.model.grid.out_of_bounds(current_pos):
            print("Posición fuera de los límites:", current_pos)
            return

        # Si hemos encontrado la salida, terminamos la simulación
        cell_contents = self.model.grid.get_cell_list_contents([current_pos])
        if any(isinstance(obj, RocaSalida) for obj in cell_contents):
            print("Bomberman ha encontrado la salida en:", current_pos)
            self.objetivo_encontrado = True  # Marcar que la salida ha sido encontrada
            self.model.terminar_simulacion()  # Terminar la simulación
            return

        # Obtener celdas vecinas según las prioridades: Arriba, Derecha, Abajo, Izquierda
        neighbors = self.get_neighbors(current_pos)

        # Buscar la primera celda vecina no visitada que sea un camino válido
        found_unvisited = False
        for neighbor in neighbors:
            if neighbor not in self.visited and self.is_valid_move(neighbor):
                self.visited.add(neighbor)  # Marcar como visitada
                self.stack.append(neighbor)  # Añadir a la pila (mover a esa posición)
                self.model.grid.move_agent(self, neighbor)  # Mover Bomberman en la grilla
                print(f"Bomberman se movió a {neighbor}")
                found_unvisited = True
                break  # Salir del bucle para moverse a la primera posición válida

        # Si no se encontró ninguna celda vecina no visitada, hacer backtracking (volver atrás)
        if not found_unvisited:
            self.stack.pop()  # Quitar la última posición de la pila (retroceder)
            if self.stack:  # Si la pila no está vacía
                prev_pos = self.stack[-1]
                self.model.grid.move_agent(self, prev_pos)  # Volver a la posición anterior
                print(f"Bomberman vuelve atrás a {prev_pos}")

    def get_neighbors(self, pos):
        x, y = pos
        # Orden de prioridades: Arriba(realmente es abajo solo que tenemos que tener en cuenta que el mapa esta invertido),
        # Derecha, Abajo(realmente es arriba por la misma razón), Izquierda
        neighbors = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
        return neighbors

    def is_valid_move(self, pos):
        # Verificar si el movimiento es válido: debe ser camino (C) o salida (R_s)
        if self.model.grid.out_of_bounds(pos):
            return False
        contents = self.model.grid.get_cell_list_contents([pos])
        return all(not isinstance(obj, (Roca, Metal)) for obj in contents)

    def step(self):
        # Verificar si la simulación sigue en ejecución
        if not self.model.running:
            return
        
        # Llamar a un solo paso del DFS en cada step del simulador
        self.dfs_step()
        
        # Verificar si Bomberman ha llegado a la salida
        if self.has_reached_exit():
            self.model.terminar_simulacion()
            

    def has_reached_exit(self):
        # Verificar si la posición actual contiene la salida
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        return any(isinstance(obj, RocaSalida) for obj in cell_contents)


    # def colocar_bomba(self):
        
    #     if self.bomba_activa:
    #         return False

    #     if self.pos is None:
    #         return False

    #     vecinos = [(self.pos[0]+dx, self.pos[1]+dy) for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]]
    #     vecinos = [v for v in vecinos if not self.model.grid.out_of_bounds(v)]
        
    #     hay_roca = False
    #     for vecino in vecinos:
    #         contenido = self.model.grid.get_cell_list_contents([vecino])
    #         if any(isinstance(obj, Roca) for obj in contenido):
    #             hay_roca = True
    #             break
        
    #     if not hay_roca:
    #         return False

    #     self.bomba_posicion = self.pos
    #     celda_segura = self.encontrar_celda_segura()
        
    #     if celda_segura:
    #         self.bomba_activa = True
    #         bomba = Bomba(self.bomba_posicion, self.model, self.poder_destruccion, self)
    #         self.model.grid.place_agent(bomba, self.bomba_posicion)
    #         self.model.schedule.add(bomba)
    #         self.model.grid.move_agent(self, celda_segura)
    #         return True
        
    #     self.bomba_posicion = None
    #     return False


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
        # Verificar si hay un Bomberman en la posición de la explosión
        contenido_celda = self.model.grid.get_cell_list_contents([self.pos])
        for obj in contenido_celda:
            if isinstance(obj, Bomberman):
                print(f"Bomberman fue alcanzado por la explosión en {self.pos}. Simulación terminada.")
                self.model.terminar_simulacion()  # Terminar la simulación si Bomberman es alcanzado
                return  # Detener la explosión si Bomberman es alcanzado
            
        self.duration -= 1
        if self.duration <= 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            
class Bomba(Agent):
    def __init__(self, pos, model, poder_destruccion, Bomberman):
        super().__init__(pos, model)
        self.pos = pos
        self.timer = poder_destruccion + 2  # Temporizador de la bomba
        self.poder_destruccion = poder_destruccion
        self.Bomberman = Bomberman  # Referencia al Bomberman que colocó la bomba

    def step(self):
        self.timer -= 1
        print(f"Temporizador de bomba en {self.timer}")  # Añade esto para verificar
        if self.timer <= 0:
            print(f"Bomba explotó en {self.pos}")
            self.explotar()
            self.model.grid.remove_agent(self)  # Eliminar la bomba del grid
            self.model.schedule.remove(self)  # Eliminar la bomba del schedule
            self.Bomberman.bomba_activa = False  # Permitir que el Bomberman coloque otra bomba

    def explotar(self):
        if self.pos is None:
            return

        x, y = self.pos
        # Variable para controlar si ya se creó una salida
        salida_creada = any(isinstance(agente, RocaSalida) for agente in self.model.schedule.agents)

        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            for alcance in range(1, self.poder_destruccion + 1):
                vecino_pos = (x + dx * alcance, y + dy * alcance)
                
                if self.model.grid.out_of_bounds(vecino_pos):
                    break

                vecinos = self.model.grid.get_cell_list_contents(vecino_pos)
                
                if any(isinstance(obj, Metal) for obj in vecinos):
                    break
                
                if any(isinstance(obj, Bomberman) for obj in vecinos):
                    print(f"Bomberman fue alcanzado por la explosión en {vecino_pos}")
                    self.model.terminar_simulacion(victoria=False)
                    return

                for obj in vecinos:
                    if isinstance(obj, Roca):
                        self.model.grid.remove_agent(obj)
                        print(f"Roca destruida en {vecino_pos}")
                        
                        # Crear salida solo si aún no existe una
                        if not salida_creada and random.random() < 0.1:
                            roca_salida = RocaSalida(vecino_pos, self.model)
                            self.model.grid.place_agent(roca_salida, vecino_pos)
                            self.model.schedule.add(roca_salida)
                            salida_creada = True
                            print(f"Salida creada en {vecino_pos}")
                        elif self.model.comodines_colocados < self.model.num_comodines:
                            comodin = Comodin(vecino_pos, self.model)
                            self.model.grid.place_agent(comodin, vecino_pos)
                            self.model.schedule.add(comodin)
                            self.model.comodines_colocados += 1
                        break

                explosion = Explosion(vecino_pos, self.model, duration=1)
                self.model.grid.place_agent(explosion, vecino_pos)
                self.model.schedule.add(explosion)

      
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