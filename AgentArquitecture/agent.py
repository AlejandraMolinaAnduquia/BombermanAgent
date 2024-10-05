from collections import deque
from model import *
import os
import sys
import time


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
        self.ruta_hacia_salida = None  # Almacenará la ruta hacia la salida

    def bfs_move(self):
        start_pos = self.pos
        print(f"Bomberman empieza en: {start_pos}")

        # Ruta del archivo posiciones_visitadas.txt
        ruta_archivo = os.path.join(os.path.dirname(__file__), '../Data/Archivos/posiciones_visitadas.txt')
        
        # Crear el directorio si no existe
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)

        # Abrir archivo para guardar las posiciones visitadas
        with open(ruta_archivo, 'w') as f:
            f.write("Posiciones visitadas:\n")
            
            # BFS para encontrar la salida
            cola = deque([start_pos])
            visitados = {start_pos}
            caminos = {start_pos: None}
            contador = 1  # Para enumerar las posiciones

            while cola:
                actual = cola.popleft()
                f.write(f"{contador}: {actual}\n")  # Guardar en el archivo
                print(f"Visitando: {actual}")
                contador += 1

                # Si llegamos a la salida, reconstruir la ruta
                if actual == self.model.find_exit():
                    self.ruta_hacia_salida = []
                    while actual:
                        self.ruta_hacia_salida.insert(0, actual)
                        actual = caminos[actual]
                    print(f"Ruta hacia la salida: {self.ruta_hacia_salida}")
                    return

                # Obtener los vecinos
                vecinos = self.get_vecinos(actual)

                for vecino in vecinos:
                    if vecino not in visitados:
                        cola.append(vecino)
                        visitados.add(vecino)
                        caminos[vecino] = actual
                        print(f"Añadiendo vecino: {vecino}")

            print("No se encontró la salida después de recorrer todos los posibles caminos.")

    def get_vecinos(self, posicion):
        x, y = posicion
        vecinos = []
        # Nuevo orden de visita: arriba, derecha, abajo, izquierda
        direcciones = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Arriba, derecha, abajo, izquierda

        for dx, dy in direcciones:
            vecino = (x + dx, y + dy)
            if not self.model.grid.out_of_bounds(vecino):
                contenido = self.model.grid.get_cell_list_contents([vecino])
                # Solo incluir celdas vacías o celdas con la salida
                if self.model.grid.is_cell_empty(vecino) or isinstance(contenido[0], RocaSalida):
                    vecinos.append(vecino)
                elif any(isinstance(obj, Roca) for obj in contenido) and not self.bomba_activa:
                    # Si hay una roca, colocar una bomba para destruirla
                    self.colocar_bomba()
        return vecinos

    def step(self):
        # Si no tiene una ruta, intentar calcularla
        if not self.ruta_hacia_salida:
            self.bfs_move()

        # Si ya tiene una ruta, seguirla
        if self.ruta_hacia_salida and len(self.ruta_hacia_salida) > 0:
            next_move = self.ruta_hacia_salida.pop(0)
            self.model.grid.move_agent(self, next_move)
            print(f"Bomberman se movió a {next_move}")

            # Verificar si ha llegado a la salida
            contenido = self.model.grid.get_cell_list_contents([self.pos])
            if any(isinstance(obj, RocaSalida) for obj in contenido):
                print("Bomberman ha llegado a la salida. ¡Juego terminado!")
                self.model.terminar_simulacion()  # Termina la simulación
        else:
            print("No hay ruta disponible o ya ha alcanzado su destino.")

        # Colocar bomba con probabilidad del 10%
        if random.random() < 0.1:
            self.colocar_bomba()

        # Recoger comodín si está en la misma celda
        self.recoger_comodin()


    def step(self):
        # Si no tiene una ruta, intentar calcularla
        if not self.ruta_hacia_salida:
            self.bfs_move()

        # Si ya tiene una ruta, seguirla
        if self.ruta_hacia_salida and len(self.ruta_hacia_salida) > 0:
            next_move = self.ruta_hacia_salida.pop(0)
            self.model.grid.move_agent(self, next_move)
            print(f"Bomberman se movió a {next_move}")

            # Verificar si ha llegado a la salida
            contenido = self.model.grid.get_cell_list_contents([self.pos])
            if any(isinstance(obj, RocaSalida) for obj in contenido):
                print("Bomberman ha llegado a la salida. ¡Juego terminado!")
                self.model.terminar_simulacion()  # Termina la simulación
        else:
            print("No hay ruta disponible o ya ha alcanzado su destino.")

        # Colocar bomba con probabilidad del 10%
        if random.random() < 0.1:
            self.colocar_bomba()

        # Recoger comodín si está en la misma celda
        self.recoger_comodin()
        

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

        self.duration -= 1
        if self.duration <= 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

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

                    # Verificar que la posición está dentro de los límites del mapa
                    if self.model.grid.out_of_bounds((vecino_x, vecino_y)):
                        break  # Salir si la celda está fuera de los límites

                    vecinos = self.model.grid.get_cell_list_contents((vecino_x, vecino_y))

                    # Detener la explosión si se encuentra con metal (Metal es indestructible)
                    if any(isinstance(obj, Metal) for obj in vecinos):
                        print(f"Explosión detenida por metal en ({vecino_x}, {vecino_y})")
                        break

                    # Si hay un comodín, la explosión lo ignora
                    if any(isinstance(obj, Comodin) for obj in vecinos):
                        print(f"Explosión ignoró el comodín en ({vecino_x}, {vecino_y})")
                        continue  # La explosión continúa su camino sin afectar el comodín

                    # Si la celda tiene una RocaSalida, la explosión no la destruye
                    if any(isinstance(obj, RocaSalida) for obj in vecinos):
                        print(f"Explosión ignoró la roca de salida en ({vecino_x}, {vecino_y})")
                        continue  # La explosión no afecta la RocaSalida

                    # Detectar si Bomberman es alcanzado por la explosión
                    if any(isinstance(obj, Bomberman) for obj in vecinos):
                        print(f"Bomberman fue alcanzado por la explosión en ({vecino_x}, {vecino_y}). Simulación terminada.")
                        self.model.terminar_simulacion()  # Termina la simulación si Bomberman es alcanzado
                        return  # Detener la explosión y la simulación

                    # Destruir rocas
                    for obj in vecinos:
                        if isinstance(obj, Roca):
                            print(f"Roca destruida en ({vecino_x}, {vecino_y})")
                            self.model.grid.remove_agent(obj)  # Eliminar la roca del grid

                            # Verificar si esta roca contenía la salida
                            if isinstance(obj, RocaSalida):
                                print(f"¡Salida descubierta en ({vecino_x}, {vecino_y})!")
                                self.model.grid.place_agent(RocaSalida((vecino_x, vecino_y), self.model), (vecino_x, vecino_y))
                                return  # Termina aquí, la salida ha sido descubierta

                            # Colocar una RocaSalida aleatoriamente (10% de probabilidad)
                            if random.random() < 0.1:  # 10% de probabilidad de crear RocaSalida
                                roca_salida = RocaSalida((vecino_x, vecino_y), self.model)
                                self.model.grid.place_agent(roca_salida, (vecino_x, vecino_y))
                                self.model.schedule.add(roca_salida)
                                print(f"Roca de salida colocada en ({vecino_x}, {vecino_y})")
                                break  # No colocar comodín si se coloca una salida

                            # Colocar un comodín si no hay salida
                            if self.model.comodines_colocados < self.model.num_comodines:
                                comodin = Comodin((vecino_x, vecino_y), self.model)
                                self.model.grid.place_agent(comodin, (vecino_x, vecino_y))
                                self.model.schedule.add(comodin)
                                self.model.comodines_colocados += 1
                                print(f"Comodín colocado en ({vecino_x, vecino_y})")
                            break  # Detener la explosión en esta dirección después de destruir la roca

                    # Si no hay roca ni metal, continuar la explosión
                    else:
                        print(f"Explosión alcanzó ({vecino_x}, {vecino_y})")
                        explosion = Explosion((vecino_x, vecino_y), self.model, duration=1)  # Pintar la explosión por 1 paso
                        self.model.grid.place_agent(explosion, (vecino_x, vecino_y))
                        self.model.schedule.add(explosion)
                        continue  # Continuar con el siguiente alcance en la misma dirección

                    break  # Detenerse al encontrar una roca o metal en la dirección actual
