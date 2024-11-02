from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import heapq

# Función para cargar el mapa desde un archivo de texto
def cargar_mapa(file_path):

    with open(file_path, 'r') as f:
        map = [line.strip().split(",") for line in f.readlines()]

    map.reverse()
    return map

# Clase de agente Bomberman
class BombermanAgent(Agent):
    def __init__(self, unique_id, model, goal):
        super().__init__(unique_id, model)
        self.goal = goal
        self.path = None  # Inicializa el camino sin calcular

    # Algoritmo A*
    def a_star(self, start, goal):
        move_cost = 10  # Costo de movimiento
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Movimientos ortogonales

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: manhattan(start, goal)}

        while open_set:
            current_f, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            for move in moves:
                neighbor = (current[0] + move[0], current[1] + move[1])
                if 0 <= neighbor[0] < self.model.grid.width and 0 <= neighbor[1] < self.model.grid.height:
                    cell_type = self.model.mapa[neighbor[0]][neighbor[1]]
                    if cell_type in ("C", "R", "R_s"):
                        tentative_g_score = g_score[current] + move_cost
                        if tentative_g_score < g_score.get(neighbor, float('inf')):
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = tentative_g_score + manhattan(neighbor, goal)
                            if neighbor not in [pos[1] for pos in open_set]:
                                heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None

    def step(self):
        # Si el camino no está calculado, cálculalo en el primer paso
        if self.path is None:
            self.path = self.a_star(self.pos, self.goal)
        if self.path:
            next_pos = self.path.pop(0)
            self.model.grid.move_agent(self, next_pos)

# Clase del modelo de Mesa
class BombermanModel(Model):
    def __init__(self, width, height, archivo_mapa):
        super().__init__()  # Inicializar la clase base Model correctamente
        self.grid = MultiGrid(width, height, True)
        self.schedule = SimultaneousActivation(self)

        # Cargar mapa
        self.mapa = cargar_mapa(archivo_mapa)
        start, goal = self.encontrar_posiciones("C_b", "R_s")

        # Colocar Bomberman en el inicio
        bomberman = BombermanAgent(1, self, goal)
        self.grid.place_agent(bomberman, start)
        self.schedule.add(bomberman)

        # Colocar obstáculos y salida
        for x in range(width):
            for y in range(height):
                if self.mapa[x][y] == "M":
                    obstacle = Agent(f"metal_{x}_{y}", self)
                    self.grid.place_agent(obstacle, (x, y))

    def step(self):
        self.schedule.step()

    # Función para encontrar posiciones de inicio y meta en el mapa
    def encontrar_posiciones(self, inicio="C_b", salida="R_s"):
        start = goal = None
        for i, fila in enumerate(self.mapa):
            for j, celda in enumerate(fila):
                if celda == inicio:
                    start = (i, j)
                elif celda == salida:
                    goal = (i, j)
        return start, goal

def rotar_mapa_90_grados(map):
    # Transponer la matriz
    transpuesta = list(zip(*map))
    # Invertir cada fila de la matriz transpuesta
    rotada = [list(reversed(fila)) for fila in transpuesta]
    return rotada

# Función para calcular distancia Manhattan
def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

# Función para visualizar el agente y los obstáculos en la interfaz
def agent_portrayal(agent):
    if isinstance(agent, BombermanAgent):
        portrayal = {"Shape": "circle", "Color": "blue", "Filled": True, "Layer": 1, "r": 0.5}
    else:  # Obstáculos
        portrayal = {"Shape": "rect", "Color": "gray", "Filled": True, "Layer": 0, "w": 0.9, "h": 0.9}
    return portrayal

# Configurar y ejecutar el servidor
width, height = 10, 10
archivo_mapa = "Data\\Maps\\mapa1.txt"
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)
server = ModularServer(BombermanModel, [grid], "Bomberman Laberinto", {"width": width, "height": height, "archivo_mapa":archivo_mapa})
server.port = 8521
server.launch()
