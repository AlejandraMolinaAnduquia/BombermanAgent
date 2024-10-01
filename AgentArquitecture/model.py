import os
import sys

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from agent import Bomberman, Roca, RocaSalida, Metal, Bomba
from Controllers.fileLoad import FileLoader


class MazeModel(Model):
    def __init__(self, width, height, num_bombermans, num_comodines, mapa_filename):
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.num_comodines = num_comodines
        self.next_id = 0  # Inicializar el contador de IDs

        # Cargar el mapa desde el archivo
        file_loader = FileLoader(mapa_filename)
        self.mapa = file_loader.cargar_mapa()

        # Inicializar el mapa
        self.inicializar_mapa()

        # Crear Bombermans
        for i in range(num_bombermans):
            poder_destruccion_inicial = 1
            bomberman = Bomberman(i, self, poder_destruccion_inicial)
            self.schedule.add(bomberman)

            # Posicionar Bomberman en el lugar especificado por "C_b"
            for y, row in enumerate(self.mapa):
                for x, cell in enumerate(row):
                    if cell == 'C_b':
                        self.grid.place_agent(bomberman, (x, y))
                        break
                    
    def next_id(self):
        self.next_id += 1
        return self.next_id

    def inicializar_mapa(self):
        # Recorre el mapa y coloca los objetos en la grilla
        for y, row in enumerate(self.mapa):
            for x, cell in enumerate(row):
                if cell == 'C':
                    # Un camino "C"
                    pass  # No se necesita acción, ya que las celdas vacías se manejan automáticamente
                elif cell == 'R':
                    # Crear una roca "R"
                    roca = Roca((x, y), self)
                    self.grid.place_agent(roca, (x, y))
                elif cell == 'R_s':
                    # Crear una roca con salida "R_s"
                    roca_salida = RocaSalida((x, y), self)
                    self.grid.place_agent(roca_salida, (x, y))
                elif cell == 'M':
                    # Crear un metal "M"
                    metal = Metal((x, y), self)
                    self.grid.place_agent(metal, (x, y))

    def step(self):
        # Avanzar un paso en la simulación
        self.schedule.step()

        
    def find_empty_cell(self):
        while True:
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            if self.grid.is_cell_empty((x, y)):
                return x, y
