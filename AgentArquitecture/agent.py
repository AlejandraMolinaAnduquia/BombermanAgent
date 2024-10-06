from collections import deque
from mesa import Agent
import random
from model import *
import os
import sys
import heapq

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Bomberman(Agent):
    def __init__(self, unique_id, model, poder_destruccion):
        super().__init__(unique_id, model)
        self.poder_destruccion = poder_destruccion
        self.bomba_activa = False
        self.ruta_hacia_salida = None
        self.stack = []
        self.visited = set()
        self.objetivo_encontrado = False
        
    def bfs_move(self):
        start_pos = self.pos
        print(f"Bomberman empieza en: {start_pos}")

        # Ruta del archivo posiciones_visitadas.txt
        ruta_archivo = os.path.join(os.path.dirname(__file__), '../Data/Archivos/posiciones_visitadas.txt')
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)

        with open(ruta_archivo, 'w') as f:
            f.write("Posiciones visitadas:\n")

            # Cola para BFS
            cola = deque([start_pos])
            visitados = {start_pos}
            caminos = {start_pos: None}
            contador = 1

            while cola:
                actual = cola.popleft()
                f.write(f"{contador}: {actual}\n")
                print(f"Visitando: {actual}")
                contador += 1

                # Verificar si ha llegado a la salida
                if self.model.find_exit() == actual:
                    self.ruta_hacia_salida = []
                    while actual:
                        self.ruta_hacia_salida.insert(0, actual)
                        actual = caminos[actual]
                    print(f"Ruta hacia la salida: {self.ruta_hacia_salida}")
                    return  # Se termina el cálculo de la ruta

                # Obtener los vecinos y añadirlos a la cola si no han sido visitados
                vecinos = self.get_vecinos(actual)
                for vecino in vecinos:
                    if vecino not in visitados:
                        cola.append(vecino)
                        visitados.add(vecino)
                        caminos[vecino] = actual
                        print(f"Añadiendo vecino: {vecino}")

        # Si no se encuentra la ruta
        if not self.ruta_hacia_salida:
            print("No se encontró una ruta hacia la salida.")
            return


    def dfs_step(self):
        if self.objetivo_encontrado:
            return

        if self.pos is None:
            self.pos = self.model.grid.find_empty()
        
        if not self.stack:
            self.stack.append(self.pos)
            self.visited.add(self.pos)

        current_pos = self.stack[-1]

        if self.model.grid.out_of_bounds(current_pos):
            return

        cell_contents = self.model.grid.get_cell_list_contents([current_pos])
        if any(isinstance(obj, RocaSalida) for obj in cell_contents):
            print("Bomberman ha encontrado la salida.")
            self.objetivo_encontrado = True
            self.model.terminar_simulacion()
            return

        neighbors = self.get_neighbors(current_pos)
        found_unvisited = False
        for neighbor in neighbors:
            if neighbor not in self.visited and self.is_valid_move(neighbor):
                self.visited.add(neighbor)
                self.stack.append(neighbor)
                self.model.grid.move_agent(self, neighbor)
                print(f"Bomberman se movió a {neighbor}")
                found_unvisited = True
                break

        if not found_unvisited:
            self.stack.pop()
            if self.stack:
                prev_pos = self.stack[-1]
                self.model.grid.move_agent(self, prev_pos)
                print(f"Bomberman vuelve atrás a {prev_pos}")

    def step(self):
        tipo_recorrido = self.model.recorrido_tipo

        if tipo_recorrido == "Anchura (BFS)":
            if not self.ruta_hacia_salida:
                self.bfs_move()
            if self.ruta_hacia_salida and len(self.ruta_hacia_salida) > 0:
                next_move = self.ruta_hacia_salida.pop(0)
                self.model.grid.move_agent(self, next_move)
                print(f"Bomberman se movió a {next_move}")
                if self.has_reached_exit():
                    self.model.terminar_simulacion()

        elif tipo_recorrido == "Profundidad (DFS)":
            self.dfs_step()

        elif tipo_recorrido == "Costo uniforme":
            if not self.ruta_hacia_salida:
                self.ucs_move()
            if self.ruta_hacia_salida and len(self.ruta_hacia_salida) > 0:
                next_move = self.ruta_hacia_salida.pop(0)
                self.model.grid.move_agent(self, next_move)
                print(f"Bomberman se movió a {next_move}")
                if self.has_reached_exit():
                    self.model.terminar_simulacion()

        self.recoger_comodin()


    def get_vecinos(self, posicion):
        x, y = posicion
        vecinos = []
        direcciones = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for dx, dy in direcciones:
            vecino = (x + dx, y + dy)
            if not self.model.grid.out_of_bounds(vecino):
                contenido = self.model.grid.get_cell_list_contents([vecino])
                if self.model.grid.is_cell_empty(vecino) or isinstance(contenido[0], RocaSalida):
                    vecinos.append(vecino)
        return vecinos

    def get_neighbors(self, pos):
        x, y = pos
        neighbors = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
        return neighbors

    def is_valid_move(self, pos):
        if self.model.grid.out_of_bounds(pos):
            return False
        contents = self.model.grid.get_cell_list_contents([pos])
        return all(not isinstance(obj, (Roca, Metal)) for obj in contents)
          

    def has_reached_exit(self):
        # Verificar si la posición actual contiene la salida
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        return any(isinstance(obj, RocaSalida) for obj in cell_contents)


    def ucs_move(self):
        start_pos = self.pos
        print(f"Bomberman comienza en: {start_pos}")

        # Cola de prioridad para UCS
        cola_prioridad = []
        heapq.heappush(cola_prioridad, (0, start_pos))  # (costo acumulado, nodo)
        visitados = {start_pos: 0}
        caminos = {start_pos: None}

        while cola_prioridad:
            costo_actual, actual = heapq.heappop(cola_prioridad)
            print(f"Expandiendo: {actual} con costo {costo_actual}")

            # Verificar si ha llegado a la salida
            if self.model.find_exit() == actual:
                self.ruta_hacia_salida = []
                while actual:
                    self.ruta_hacia_salida.insert(0, actual)
                    actual = caminos[actual]
                print(f"Ruta hacia la salida encontrada: {self.ruta_hacia_salida}")
                return

            # Obtener vecinos y calcular el costo
            vecinos = self.get_vecinos(actual)
            for vecino in vecinos:
                contenido = self.model.grid.get_cell_list_contents([vecino])
                costo_movimiento = 1  # Asignar costo diferente para celdas (esto puede ajustarse)

                nuevo_costo = costo_actual + costo_movimiento
                if vecino not in visitados or nuevo_costo < visitados[vecino]:
                    visitados[vecino] = nuevo_costo
                    caminos[vecino] = actual
                    heapq.heappush(cola_prioridad, (nuevo_costo, vecino))
                    print(f"Añadiendo vecino: {vecino} con costo acumulado: {nuevo_costo}")

        print("No se encontró la salida después de recorrer todos los caminos posibles.")


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

class Comodin(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos

    def step(self):
        pass  # El comodín no hace nada en cada paso

      
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
