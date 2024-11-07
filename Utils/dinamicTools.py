import tkinter as tk
from tkinter import filedialog

def load_map(file_path):
    """
    Carga un mapa desde un archivo y lo convierte en una estructura de lista de listas.
    
    Args:
        file_path (str): La ruta del archivo del mapa a cargar.
        
    Returns:
        list of list of str: Mapa representado como una lista de listas de strings.
    """
    # Abre el archivo y lee cada línea, dividiendo en una lista por cada coma.
    with open(file_path, 'r') as f:
        map = [line.strip().split(",") for line in f.readlines()]

    # Invertir el mapa verticalmente para una visualización consistente
    map.reverse()
    return map


def get_map_path():
    """
    Abre un cuadro de diálogo para seleccionar un archivo de mapa usando `tkinter`.

    Returns:
        str: La ruta del archivo seleccionado por el usuario, o None si se cancela.
    """
    # Inicializa la ventana de `tkinter` en modo oculto.
    root = tk.Tk()
    root.withdraw()
    
    # Abre un cuadro de diálogo para seleccionar un archivo de texto
    map_path = filedialog.askopenfilename(
        title="Select the map file",
        filetypes=[("Text Files", "*.txt")]
    )
    
    # Cierra la ventana de `tkinter`
    root.destroy()
    return map_path
