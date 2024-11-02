from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from IdentityArquitecture.agents import AgentIdentity
from SearchesArquitecture.UninformedSearches.dfs import dfs
from SearchesArquitecture.UninformedSearches.bfs import bfs
from SearchesArquitecture.UninformedSearches.ucs import ucs
from AgentArquitecture.bomberman import BombermanAgent
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.globe import GlobeAgent
from AgentArquitecture.road import RoadAgent
from SearchesArquitecture.InformedSearches.astar import AStarSearch
from Utils.dinamicTools import load_map, get_map_path

class MazeModel(Model):
    def __init__(self, width, height, map, search_strategy):
        super().__init__()
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.globe_active = True
        self.goal_position = None  # Inicializar la posición objetivo

        if search_strategy == "DFS":
            search_strategy = dfs()
        elif search_strategy == "BFS":
            search_strategy = bfs()
        elif search_strategy == "UCS":
            search_strategy = ucs()
        elif search_strategy == "A*":
            search_strategy = AStarSearch()

        for y, row in enumerate(map):
            for x, cell in enumerate(row):
                if cell == "C":
                    road = AgentIdentity.create_agent("road", (x, y), self)
                    self.grid.place_agent(road, (x, y))
                    self.schedule.add(road)
                elif cell == "M":
                    metal = AgentIdentity.create_agent("metal", (x, y), self)
                    self.grid.place_agent(metal, (x, y))
                    self.schedule.add(metal)
                elif cell == "R":
                    rock = AgentIdentity.create_agent("rock", (x, y), self)
                    self.grid.place_agent(rock, (x, y))
                    self.schedule.add(rock)
                elif cell == "C_b":
                    road = AgentIdentity.create_agent("road", (x, y), self)
                    self.grid.place_agent(road, (x, y))
                    self.schedule.add(road)
                    road.is_visited = True
                    bomberman = AgentIdentity.create_agent("bomberman", (x, y), self, search_strategy)
                    self.grid.place_agent(bomberman, (x, y))
                    self.schedule.add(bomberman)
                elif cell == "R_s":
                    goal = AgentIdentity.create_agent("goal", (x, y), self)
                    self.grid.place_agent(goal, (x, y))
                    self.schedule.add(goal)
                    self.goal_position = (x, y)  # Asignar la posición del objetivo

                elif cell == "G":
                    globe = AgentIdentity.create_agent("globe", (x, y), self)
                    self.grid.place_agent(globe, (x, y))
                    self.schedule.add(globe)
        self.running = True
        

    def step(self):
        self.schedule.step()
        self.check_bomberman_and_goal()

    def check_bomberman_and_goal(self):
        for cell in self.grid.coord_iter():
            cell_content, (x, y) = cell
            bomberman_present = any(isinstance(agent, BombermanAgent) for agent in cell_content)
            goal_present = any(isinstance(agent, GoalAgent) for agent in cell_content)
            if bomberman_present and goal_present:
                self.running = False
                break
    
    def is_cell_empty(self, position):
        cell_content = self.grid.get_cell_list_contents([position])
        return all(isinstance(agent, (RoadAgent, GoalAgent)) for agent in cell_content)
    
    def reset_game(self):
        # Restablecer las posiciones iniciales de Bomberman, globos y otros elementos del mapa
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.grid.width, self.grid.height, True)

        # Volver a colocar a Bomberman y a los globos en sus posiciones iniciales
        bomberman = BombermanAgent(self.next_id(), self, self.search_strategy)
        self.grid.place_agent(bomberman, (1, 1))  # Cambia esta posición según sea necesario
        self.schedule.add(bomberman)

        for pos in self.initial_globe_positions:
            globe = GlobeAgent(self.next_id(), self)
            self.grid.place_agent(globe, pos)
            self.schedule.add(globe)

        # Cargar otros agentes, como caminos
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                if self.grid.is_cell_empty((x, y)):
                    road = RoadAgent(self.next_id(), self)
                    self.grid.place_agent(road, (x, y))
                    self.schedule.add(road)
    
    def reset_game(self):
        """Reinicia el juego recargando el mapa desde el archivo original."""
        # Obtener el nuevo mapa y reiniciar agentes
        self.schedule = RandomActivation(self)
        new_map_path = get_map_path()  # Llama al diálogo para obtener el archivo
        if new_map_path:
            new_map = load_map(new_map_path)
            self.grid = MultiGrid(len(new_map[0]), len(new_map), True)
            self.load_agents_from_map(new_map)