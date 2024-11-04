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
from SearchesArquitecture.InformedSearches.beamsearch import BeamSearch
from SearchesArquitecture.InformedSearches.hillclimbing import HillClimbing
from Utils.dinamicTools import load_map, get_map_path

class MazeModel(Model):
    def __init__(self, width, height, map, search_strategy, beta: int = None):
        super().__init__()
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.globe_active = True
        self.goal_position = None
        self.search_strategy = None

        if search_strategy == "DFS":
            search_strategy = dfs()
        elif search_strategy == "BFS":
            search_strategy = bfs()
        elif search_strategy == "UCS":
            search_strategy = ucs()
        elif search_strategy == "A*":
            search_strategy = AStarSearch()
        elif search_strategy == "Beam Search":
            search_strategy = BeamSearch(beta)
        elif search_strategy == "Hill Climbing":
            search_strategy = HillClimbing()

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
                    self.goal_position = (x, y) 
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
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.grid.width, self.grid.height, True)
        bomberman = BombermanAgent(self.next_id(), self, self.search_strategy)
        self.grid.place_agent(bomberman, (1, 1)) 
        self.schedule.add(bomberman)

        for pos in self.initial_globe_positions:
            globe = GlobeAgent(self.next_id(), self)
            self.grid.place_agent(globe, pos)
            self.schedule.add(globe)

        for x in range(self.grid.width):
            for y in range(self.grid.height):
                if self.grid.is_cell_empty((x, y)):
                    road = RoadAgent(self.next_id(), self)
                    self.grid.place_agent(road, (x, y))
                    self.schedule.add(road)