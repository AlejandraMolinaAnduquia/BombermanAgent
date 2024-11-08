from SearchesArquitecture.searchStrategy import SearchStrategy
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
import heapq
import math

class AStarSearch(SearchStrategy):
    def __init__(self, heuristic='Manhattan'):
        self.open_set = []
        self.visited = set()
        self.g_score = {}
        self.f_score = {}
        self.step_count = 0
        self.index = 0
        self.heuristic = heuristic
        self.weight = 1.0  # Factor de peso para la heurística

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def euclidean_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def start_search(self, start, goal):
        self.goal = goal
        self.open_set = []
        self.visited.clear()
        self.g_score.clear()
        self.f_score.clear()
        
        self.g_score[start] = 0
        h_score = self.manhattan_distance(start, goal) if self.heuristic == 'Manhattan' else self.euclidean_distance(start, goal)
        h_score *= self.weight  # Aplicar peso a la heurística
        self.f_score[start] = h_score
        
        heapq.heappush(self.open_set, (h_score, 0, self.index, start, [start]))
        self.step_count = 0

    def is_valid_move(self, pos, agent):
        x, y = pos
        if not (0 <= x < agent.model.grid.width and 0 <= y < agent.model.grid.height):
            return False
            
        agents_in_cell = agent.model.grid[x][y]
        return all(isinstance(a, (RoadAgent, GoalAgent, RockAgent, GlobeAgent)) for a in agents_in_cell)

    def get_neighbors(self, pos):
        # Definir el orden de preferencia para la expansión
        x, y = pos
        return [
            (x-1, y),  # Arriba
            (x, y+1),  # Derecha
            (x+1, y),  # Abajo
            (x, y-1)   # Izquierda
        ]

    def explore_step(self, agent, diagonal=False):
        if not self.open_set:
            return None

        _, g_score, _, current, path = heapq.heappop(self.open_set)
        
        if current in self.visited:
            return current

        self.step_count += 1
        print(f"Expandiendo nodo {self.step_count}: {current}, Camino acumulado hasta ahora: {path}")
        
        agents_in_cell = agent.model.grid[current[0]][current[1]]
        if any(isinstance(a, GoalAgent) for a in agents_in_cell):
            agent.path_to_exit = path
            agent.has_explored = True
            print("Meta alcanzada. Camino óptimo calculado:", path)
            return None

        self.visited.add(current)
        agent.model.grid[current[0]][current[1]][0].visit_order = self.step_count

        # Usar get_neighbors para mantener el orden de expansión consistente
        for next_pos in self.get_neighbors(current):
            if not self.is_valid_move(next_pos, agent) or next_pos in self.visited:
                continue

            tentative_g_score = g_score + 1

            if next_pos not in self.g_score or tentative_g_score < self.g_score[next_pos]:
                self.g_score[next_pos] = tentative_g_score
                h_score = (self.manhattan_distance(next_pos, self.goal) 
                          if self.heuristic == 'Manhattan' 
                          else self.euclidean_distance(next_pos, self.goal))
                h_score *= self.weight
                
                f_score = tentative_g_score + h_score
                self.f_score[next_pos] = f_score
                
                self.index += 1
                heapq.heappush(self.open_set, (f_score, tentative_g_score, self.index, next_pos, path + [next_pos]))

        return current