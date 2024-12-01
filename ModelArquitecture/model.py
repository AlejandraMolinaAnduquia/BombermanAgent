# Importaciones necesarias para el modelo y sus agentes
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
from AgentArquitecture.bomb import BombAgent
from AgentArquitecture.explosion import ExplosionAgent
from AgentArquitecture.powerup import PowerupAgent
from SearchesArquitecture.InformedSearches.astar import AStarSearch
from SearchesArquitecture.InformedSearches.beamsearch import BeamSearch
from SearchesArquitecture.InformedSearches.hillclimbing import HillClimbing
from Utils.dinamicTools import load_map, get_map_path
from SearchesArquitecture.InformedSearches.astar import AStarSearch
from SearchesArquitecture.InformedSearches.alphabeta import AlphaBetaSearch

class MazeModel(Model):
    """
    Clase de simulación de un modelo de laberinto donde Bomberman debe encontrar
    un camino óptimo hacia un objetivo, evitando obstáculos y enemigos.

    Métodos:
        __init__: Inicializa el modelo con el mapa, los agentes y la estrategia de búsqueda.
        step: Ejecuta un paso en la simulación.
        check_bomberman_and_goal: Verifica si Bomberman ha alcanzado el objetivo.
        is_cell_empty: Comprueba si una celda contiene solo caminos o el objetivo.
        reset_game: Reinicia el juego en su configuración inicial.
    """

    def __init__(self, width, height, map, search_strategy, distance_metric="Manhattan",beta: int = None, level: int = 0):
        """
        Inicializa el modelo de laberinto con la configuración proporcionada.

        Args:
            width (int): Ancho de la cuadrícula.
            height (int): Altura de la cuadrícula.
            map (list): Mapa del laberinto con códigos para cada tipo de agente.
            search_strategy (str): Estrategia de búsqueda elegida (p.ej., "DFS", "A*").
            beta (int, opcional): Parámetro usado en la búsqueda de haz (Beam Search).
        """
        super().__init__()
        self.grid = MultiGrid(width, height, True)  # Configura la cuadrícula del laberinto.
        self.schedule = RandomActivation(self)      # Inicializa el programador de activación aleatoria.
        self.globe_active = True                    # Indica si los globos están activos.
        self.goal_position = None                   # Almacena la posición del objetivo.
        self.search_strategy = None                 # Estrategia de búsqueda seleccionada.
        self.turn = "Bomberman"  # Inicializa el turno para Bomberman
        self.level = level  # Nivel de dificultad de los globos

        # Asigna la estrategia de búsqueda según la elección del usuario
        if search_strategy == "DFS":
            self.search_strategy = dfs()
        elif search_strategy == "BFS":
            self.search_strategy = bfs()
        elif search_strategy == "UCS":
            self.search_strategy = ucs()
        elif search_strategy == "A*":
            self.search_strategy = AStarSearch(heuristic=distance_metric)
        elif search_strategy == "Beam Search":
            self.search_strategy = BeamSearch(beta, heuristic=distance_metric)
        elif search_strategy == "Hill Climbing":
            self.search_strategy = HillClimbing(heuristic=distance_metric)
        elif search_strategy == "Alpha-Beta":
            self.search_strategy = AlphaBetaSearch(3)
        else:
            raise ValueError(f"Estrategia de búsqueda desconocida: {search_strategy}")


        # Configuración de la cuadrícula y agentes
        for y, row in enumerate(map):
            for x, cell in enumerate(row):
                # Inicializa los agentes en la cuadrícula según el tipo de celda
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
                    bomberman = AgentIdentity.create_agent("bomberman", (x, y), self, self.search_strategy)
                    self.grid.place_agent(bomberman, (x, y))
                    self.schedule.add(bomberman)
                elif cell == "R_s":
                    goal = AgentIdentity.create_agent("goal", (x, y), self)
                    self.grid.place_agent(goal, (x, y))
                    self.schedule.add(goal)
                    self.goal_position = (x, y)
                elif cell == "C_g":
                    globe = AgentIdentity.create_agent("globe", (x, y), self)
                    self.grid.place_agent(globe, (x, y))
                    self.schedule.add(globe)
        
        self.running = True

    def step(self):
        """
        Ejecuta un paso en la simulación, activando cada agente y luego
        verificando si Bomberman ha alcanzado el objetivo.
        """
        if isinstance(self.search_strategy, AlphaBetaSearch):
            if self.turn == "Bomberman":
                # Activar solo Bomberman
                for agent in self.schedule.agents:
                    if isinstance(agent, BombermanAgent):
                        agent.step()
                    if isinstance(agent, BombAgent):
                        agent.step()
                    if isinstance(agent, ExplosionAgent):
                        agent.step()
                    if isinstance(agent, PowerupAgent):
                        agent.step()
                self.turn = "Globes"  # Cambiar el turno a los globos
            elif self.turn == "Globes":
                # Activar solo los globos
                for agent in self.schedule.agents:
                    if isinstance(agent, GlobeAgent):
                        agent.step()
                self.turn = "Bomberman"  # Cambiar el turno a Bomberman
        else:
            # Activar todos los agentes
            self.schedule.step()

        self.check_bomberman_and_goal()  # Verifica si el objetivo ha sido alcanzado


    def check_bomberman_and_goal(self):
        """
        Recorre la cuadrícula para verificar si Bomberman ha alcanzado el objetivo.
        Si es así, detiene la simulación.
        """
        for cell in self.grid.coord_iter():
            cell_content, (x, y) = cell  # Obtiene contenido y posición de cada celda
            # Verifica si Bomberman y el objetivo están en la misma celda
            bomberman_present = any(isinstance(agent, BombermanAgent) for agent in cell_content)
            goal_present = any(isinstance(agent, GoalAgent) for agent in cell_content)
            if bomberman_present and goal_present:
                self.running = False  # Detiene la simulación si Bomberman ha alcanzado el objetivo
                break

    def is_cell_empty(self, position):
        """
        Comprueba si una celda específica contiene solo caminos o el objetivo,
        lo cual indica que está disponible para moverse.

        Args:
            position (tuple): Coordenadas de la celda a verificar.

        Returns:
            bool: `True` si la celda está vacía de obstáculos, `False` en caso contrario.
        """
        cell_content = self.grid.get_cell_list_contents([position])
        # Verifica que la celda contenga solo agentes de camino o el objetivo
        return all(isinstance(agent, (RoadAgent, GoalAgent)) for agent in cell_content)

    def reset_game(self):
        """
        Reinicia el juego, restaurando la cuadrícula y los agentes a su configuración inicial.
        """
        # Reinicia el programador y la cuadrícula
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.grid.width, self.grid.height, True)
        
        # Coloca a Bomberman en la posición inicial
        bomberman = BombermanAgent(self.next_id(), self, self.search_strategy)
        self.grid.place_agent(bomberman, (1, 1))
        self.schedule.add(bomberman)

        # Restablece los globos en sus posiciones iniciales
        for pos in self.initial_globe_positions:
            globe = GlobeAgent(self.next_id(), self)
            self.grid.place_agent(globe, pos)
            self.schedule.add(globe)

        # Coloca caminos en las celdas vacías de la cuadrícula
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                if self.grid.is_cell_empty((x, y)):
                    road = RoadAgent(self.next_id(), self)
                    self.grid.place_agent(road, (x, y))
                    self.schedule.add(road)