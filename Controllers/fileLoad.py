import os
import sys

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FileLoader:
    def __init__(self, filename):
        self.filename = filename

    def cargar_mapa(self):
        with open(self.filename, 'r') as file:
            mapa = [line.strip().split(',') for line in file.readlines()]
            
        # Invertir las filas del mapa
        mapa_invertido = mapa[::-1]
        
        return mapa_invertido
