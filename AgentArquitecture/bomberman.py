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
        self.retreat_steps = 0  # Pasos para retroceder antes de la explosión
        self.direction = (0, 0)
        self.previous_pos = None 

    def place_bomb(self):
        from AgentArquitecture.bomb import BombAgent
        if self.waiting_for_explosion:
            return  # Ya hay una bomba activa, no coloca otra

        bomb = BombAgent(self.model.next_id(), self.model, self.pos, self.destruction_power)
        self.model.grid.place_agent(bomb, self.pos)
        self.model.schedule.add(bomb)
        self.waiting_for_explosion = True
        self.bomb_position = self.pos
        self.steps_to_explosion = self.destruction_power + 2
        self.retreat_steps = self.destruction_power + 1
        print(f"Bomba colocada en la posición: {self.bomb_position} con poder de destrucción: {self.destruction_power}")

    def collect_powerup(self):
        """Verifica si hay un PowerupAgent en la posición actual y lo recoge."""
        from AgentArquitecture.powerup import PowerupAgent
        agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])
        
        for agent in agents_in_cell:
            if isinstance(agent, PowerupAgent):
                self.destruction_power += 1
                self.model.grid.remove_agent(agent)
                self.model.schedule.remove(agent)
                print(f"Comodín recogido en la posición: {self.pos}. Poder de destrucción aumentado a {self.destruction_power}.")

    def move_to_position(self, next_position):
        """Mueve a Bomberman a la posición siguiente y recoge cualquier comodín presente."""
        self.model.grid.move_agent(self, next_position)
        print(f"Moviéndose a la posición: {self.pos}")
        self.collect_powerup()  # Recoge el comodín si está en la nueva posición

    def retreat_on_optimal_path(self):
        """Retrocede sobre el camino óptimo para esconderse de la explosión."""
        if self.retreat_steps > 0 and self.original_path:
            current_index = self.original_path.index(self.pos)
            retreat_index = max(current_index - self.retreat_steps, 0)
            retreat_path = self.original_path[retreat_index:current_index][::-1]
            
            if retreat_path:
                next_position = retreat_path.pop(0)
                if self.is_adjacent(self.pos, next_position):
                    self.move_to_position(next_position)
                else:
                    print(f"Error: Movimiento diagonal detectado en el retroceso, entre {self.pos} y {next_position}.")
            self.retreat_steps -= 1

    def resume_optimal_path(self):
        """Reanuda el camino óptimo desde la posición actual."""
        self.steps_to_explosion = self.destruction_power + 2  # Ajusta el tiempo hasta la explosión

    def find_closest_safe_position(self):
        from AgentArquitecture.road import RoadAgent
        """Encuentra la posición más cercana segura para evitar la explosión."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
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
                if (
                    not self.model.grid.out_of_bounds(next_position) and
                    next_position not in visited
                ):
                    agents_in_next_position = self.model.grid.get_cell_list_contents([next_position])
                    if all(isinstance(agent, RoadAgent) for agent in agents_in_next_position):
                        queue.append((next_position, path + [next_position]))
        return []

    def find_nearest_point_on_path(self):
        """Encuentra el punto en `original_path` más cercano a la posición actual de Bomberman."""
        min_distance = float('inf')
        nearest_point_index = 0
        for i, point in enumerate(self.original_path):
            distance = abs(self.pos[0] - point[0]) + abs(self.pos[1] - point[1])
            if distance < min_distance:
                min_distance = distance
                nearest_point_index = i
                
        return self.original_path[nearest_point_index:]


    def resume_from_current_position(self):
        """Restaura `path_to_exit` desde el punto más cercano en el camino original."""
        if self.pos in self.original_path:
            current_index = self.original_path.index(self.pos)
            self.path_to_exit = self.original_path[current_index + 1:]

    def is_adjacent(self, pos1, pos2):
        """Verifica si `pos2` está en una casilla adyacente ortogonal a `pos1`."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1


    def move_to_exit_or_safety(self):
        from AgentArquitecture.rock import RockAgent
        from AgentArquitecture.metal import MetalAgent
        from AgentArquitecture.bomb import BombAgent

        if self.waiting_for_explosion:
            if self.steps_to_explosion > 0:
                self.steps_to_explosion -= 1
                self.retreat_on_optimal_path()
            else:
                agents_in_bomb_cell = self.model.grid.get_cell_list_contents([self.bomb_position])
                if not any(isinstance(agent, BombAgent) for agent in agents_in_bomb_cell):
                    self.waiting_for_explosion = False
                    self.bomb_position = None
                    print("Explosión completada, retomando el camino óptimo.")
                    self.resume_optimal_path()
            return

        if self.path_to_exit:
            next_position = self.path_to_exit.pop(0)
            agents_in_cell = self.model.grid.get_cell_list_contents([next_position])

            if all(not isinstance(agent, (RockAgent, MetalAgent, BombAgent)) for agent in agents_in_cell):
                self.move_to_position(next_position)

            elif any(isinstance(agent, RockAgent) for agent in agents_in_cell):
                self.place_bomb()
                

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
        print(f"Posición actual de Bomberman en este paso: {self.pos}")

