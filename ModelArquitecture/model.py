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

class MazeModel(Model):
    def __init__(self, width, height, map, search_strategy):
        super().__init__()
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        if search_strategy == "DFS":
            search_strategy = dfs()
        elif search_strategy == "BFS":
            search_strategy = bfs()
        elif search_strategy == "UCS":
            search_strategy = ucs()

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