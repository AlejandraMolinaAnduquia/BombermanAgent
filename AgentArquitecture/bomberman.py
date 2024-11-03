from mesa import Agent

class BombermanAgent(Agent):
    def __init__(self, unique_id, model, search_strategy):
        super().__init__(unique_id, model)
        self.search_strategy = search_strategy
        self.path_to_exit = []
        self.has_explored = False
        self.is_search_initialized = False
        self.is_moving = False
        self.destruction_power = 1  # Poder inicial de destrucción
        self.waiting_for_explosion = False  # Indica si Bomberman está esperando a que la bomba explote
        self.bomb_position = None  # Almacena la posición de la última bomba colocada
        self.steps_to_explosion = 0  # Contador de tiempo hasta la explosión de la bomba
        self.original_path = []  # Guarda el camino óptimo calculado inicialmente
        self.direction = (0, 0)
        self.previous_pos = None 
        self.pos = (0, 0)

    def place_bomb(self):
        from AgentArquitecture.bomb import BombAgent
        """Coloca una bomba en la posición actual de Bomberman si no está esperando otra explosión."""
        if self.waiting_for_explosion:
            return  # Ya hay una bomba activa, no coloca otra

        # Coloca la bomba y configura la espera para la explosión
        bomb = BombAgent(self.model.next_id(), self.model, self.pos, self.destruction_power)
        self.model.grid.place_agent(bomb, self.pos)
        self.model.schedule.add(bomb)
        self.waiting_for_explosion = True
        self.bomb_position = self.pos
        self.steps_to_explosion = self.destruction_power + 2  # Ajusta el tiempo hasta la explosión

    def find_closest_safe_position(self):
        from AgentArquitecture.road import RoadAgent
        """Encuentra la posición más cercana segura para evitar la explosión."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Movimientos ortogonales
        queue = [(self.pos, [])]
        visited = set()

        while queue:
            current_position, path = queue.pop(0)
            if current_position in visited:
                continue
            visited.add(current_position)

            # Verifica si está fuera del alcance de la explosión
            if self.bomb_position is not None:
                distance_to_bomb = abs(current_position[0] - self.bomb_position[0]) + abs(current_position[1] - self.bomb_position[1])
                if distance_to_bomb > self.destruction_power:
                    return path  # Retorna el camino a la primera posición segura encontrada

            # Explora celdas adyacentes
            for direction in directions:
                next_position = (current_position[0] + direction[0], current_position[1] + direction[1])
                if (not self.model.grid.out_of_bounds(next_position) and 
                        next_position not in visited):
                    agents_in_next_position = self.model.grid.get_cell_list_contents([next_position])
                    if all(isinstance(agent, RoadAgent) for agent in agents_in_next_position):
                        queue.append((next_position, path + [next_position]))
        return []

    def find_nearest_point_on_path(self):
        if self.pos is None:
            return None  # Manejo de caso no válido
        nearest_point = min(self.path_to_exit, key=lambda point: abs(self.pos[0] - point[0]) + abs(self.pos[1] - point[1]), default=None)
        return nearest_point

    def resume_from_current_position(self):
        """Restaura `path_to_exit` desde el punto más cercano en el camino original."""
        if self.pos in self.original_path:
            # Si está en el camino óptimo, retoma desde esta posición
            current_index = self.original_path.index(self.pos)
            self.path_to_exit = self.original_path[current_index + 1:]
        else:
            # Si no está en el camino, encuentra el punto más cercano y ajusta el camino
            self.path_to_exit = self.find_nearest_point_on_path()

    def move_to_exit_or_safety(self):
        """Controla el movimiento de Bomberman hacia la salida o hacia una posición segura si está evitando la explosión."""
        from AgentArquitecture.rock import RockAgent
        from AgentArquitecture.metal import MetalAgent
        from AgentArquitecture.bomb import BombAgent
        
        if self.pos is None or not self.path_to_exit:
            return  # Manejo de caso no válido

        next_position = self.path_to_exit[0]  # Ajusta esto según tu lógica
        self.direction = (next_position[0] - self.pos[0], next_position[1] - self.pos[1])

        # Si está esperando la explosión, sigue el camino hacia una posición segura
        if self.waiting_for_explosion:
            if self.steps_to_explosion > 0:
                self.steps_to_explosion -= 1
            else:
                # Verifica si la bomba ha explotado
                agents_in_bomb_cell = self.model.grid.get_cell_list_contents([self.bomb_position])
                if not any(isinstance(agent, BombAgent) for agent in agents_in_bomb_cell):
                    # La bomba ha explotado, permite retomar el camino sin teletransportarse
                    self.waiting_for_explosion = False
                    self.bomb_position = None
                    self.resume_from_current_position()  # Retoma desde el punto más cercano

            if self.path_to_exit:
                next_position = self.path_to_exit.pop(0)
                self.previous_pos = self.pos 
                self.direction = (next_position[0] - self.pos[0], next_position[1] - self.pos[1])  
                self.model.grid.move_agent(self, next_position)
            return

        # Verifica si la celda siguiente tiene obstáculos
        agents_in_cell = self.model.grid.get_cell_list_contents([next_position])
        if any(isinstance(agent, RockAgent) for agent in agents_in_cell):
            self.place_bomb()
            safe_path = self.find_closest_safe_position()
            if safe_path:
                self.path_to_exit = safe_path  
            return

        if all(
            not isinstance(agent, (RockAgent, MetalAgent, BombAgent)) for agent in agents_in_cell
        ):
            self.path_to_exit.pop(0)
            self.previous_pos = self.pos 
            self.direction = (next_position[0] - self.pos[0], next_position[1] - self.pos[1]) 
            self.model.grid.move_agent(self, next_position)
            self.is_moving = True

    def step(self):
        """Realiza un paso en la simulación."""
        if not self.is_search_initialized:
            start_position = (self.pos[0], self.pos[1])
            self.search_strategy.start_search(start_position, self.model.goal_position)
            self.is_search_initialized = True

        if not self.has_explored:
            self.search_strategy.explore_step(self)
            if self.has_explored:
                print("Camino óptimo calculado:", self.path_to_exit)
                self.original_path = self.path_to_exit[:]  
            return

        self.move_to_exit_or_safety()
