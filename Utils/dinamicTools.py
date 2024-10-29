import tkinter as tk
from tkinter import filedialog

def load_map(file_path):
    with open(file_path, 'r') as f:
        map = [line.strip().split(",") for line in f.readlines()]

    map.reverse()
    return map

def get_map_path():
    root = tk.Tk()
    root.withdraw()
    map_path = filedialog.askopenfilename(
        title="Select the map file",
        filetypes=[("Text Files", "*.txt")]
    )
    root.destroy()
    return map_path