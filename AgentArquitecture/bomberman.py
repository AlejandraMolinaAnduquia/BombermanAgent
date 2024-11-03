from mesa import Agent

class BombermanAgent(Agent):
    def __init__(self, unique_id, model, search_strategy):
        super().__init__(unique_id, model)
        self.search_strategy = search_strategy
        self.path_to_exit = []
        self.has_explored = False
        self.is_search_initialized = False
        self.is_moving = False
        self.destruction_power = 1  
        self.waiting_for_explosion = False  
        self.bomb_position = None  
        self.steps_to_explosion = 0  
        self.original_path = [] 
        self.retreat_steps = 0 
        self.direction = (0, 0) 
        
        self.directions = {
                'UP': (0, -1),
                'DOWN': (0, 1),
                'LEFT': (-1, 0),
                'RIGHT': (1, 0),
            }

    def calculate_direction(self):
        """Determina la dirección en la que se moverá Bomberman."""
        if self.is_moving:
            return self.directions['UP'] 
        return self.direction
    
    def place_bomb(self):
        from AgentArquitecture.bomb import BombAgent
        if self.waiting_for_explosion:
            return  

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
        
        if next_position is not None:
            self.model.grid.move_agent(self, next_position)
            self.is_moving = True 
            print(f"Moviéndose a la posición: {self.pos}")
            self.collect_powerup()  
        else:
            print("Error: next_position es None o no válido.")



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
                self.is_moving = False
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
        
        self.direction = self.calculate_direction() 
        if not self.has_explored:
            self.search_strategy.explore_step(self)
            if self.has_explored:
                print("Camino óptimo calculado:", self.path_to_exit)
                self.original_path = self.path_to_exit[:]
            return

        self.move_to_exit_or_safety()
        print(f"Posición actual de Bomberman en este paso: {self.pos}")