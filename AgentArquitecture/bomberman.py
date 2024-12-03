from mesa import Agent
from Utils.state import GameState
from SearchesArquitecture.InformedSearches.alphabeta import AlphaBetaSearch


class BombermanAgent(Agent):
    def __init__(self, unique_id, model, search_strategy):
        """
        Inicializa al agente Bomberman con parámetros iniciales de estado y atributos específicos,
        incluidos los relacionados con la colocación de bombas, movimientos y el seguimiento del camino óptimo.

        Args:
            unique_id: Identificador único del agente.
            model: El modelo al que pertenece el agente.
            search_strategy: Estrategia de búsqueda para calcular el camino óptimo hacia la salida.
        """
        super().__init__(unique_id, model)
        self.search_strategy = search_strategy  # Estrategia de búsqueda para el camino óptimo
        self.path_to_exit = []  # Almacena el camino óptimo calculado hacia la salida
        self.has_explored = False
        self.is_search_initialized = False  # Estado para indicar si se ha inicializado la búsqueda
        self.is_moving = False
        self.destruction_power = 1  # Poder de destrucción inicial de Bomberman
        self.waiting_for_explosion = False  # Estado de espera para explosión de bomba
        self.bomb_position = None
        self.steps_to_explosion = 0
        self.original_path = []  # Almacena una copia del camino óptimo
        self.retreat_steps = 0  # Controla los pasos de retroceso en el camino óptimo
        self.direction = (0, 0)  # Dirección inicial de movimiento
        self.alpha_beta = AlphaBetaSearch(max_depth=3)  # Configurar profundidad de búsqueda

        if model is not None:
            model.register_agent(self)  # Solo registra si hay modelo


        # Direcciones posibles de movimiento de directions = [(-1, 0), (0, 1), (1, 0), (0, -1)] Bomberman Prioridad: Izquierda, Arriba, Derecha, Abajo
        self.directions = {
            'UP': (0, 1),
            'DOWN': (0, -1),
            'LEFT': (-1, 0),
            'RIGHT': (1, 0),
        }

    def calculate_direction(self):
        """
        Calcula y devuelve la dirección de movimiento de Bomberman.
        Retorna 'UP' si está en movimiento; de lo contrario, conserva la dirección actual.
        """
        if self.is_moving:
            return self.directions['UP']
        return self.direction
    
    def place_bomb(self):
        """
        Coloca una bomba en la posición actual de Bomberman y configura el temporizador
        de explosión basado en el poder de destrucción. Marca a Bomberman en estado de espera
        de explosión, evitando que se mueva o coloque otra bomba.
        """
        from AgentArquitecture.bomb import BombAgent
        if self.waiting_for_explosion:
            return  # Evita colocar otra bomba si ya hay una en espera de explotar

        # Crea la bomba en la posición actual de Bomberman
        bomb = BombAgent(self.model.next_id(), self.model, self.pos, self.destruction_power)
        self.model.grid.place_agent(bomb, self.pos)
        self.model.schedule.add(bomb)
        self.waiting_for_explosion = True  # Establece el estado de espera para la explosión
        self.bomb_position = self.pos
        self.steps_to_explosion = self.destruction_power + 2
        self.retreat_steps = self.destruction_power + 1
        print(f"Bomba colocada en la posición: {self.bomb_position} con poder de destrucción: {self.destruction_power}")

    def collect_powerup(self):
        """
        Recoge un powerup en la posición actual, incrementando el poder de destrucción
        de Bomberman y reemplazando el PowerupAgent con un RoadAgent en el camino óptimo.
        """
        from AgentArquitecture.powerup import PowerupAgent
        from AgentArquitecture.road import RoadAgent
        agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])
        
        for agent in agents_in_cell:
            if isinstance(agent, PowerupAgent):
                # Incrementa el poder de destrucción de Bomberman
                self.destruction_power += 1
                print(f"Comodín recogido en la posición: {self.pos}. Poder de destrucción aumentado a {self.destruction_power}.")

                # Captura el número de orden de visita antes de eliminar el PowerupAgent
                visit_order = agent.original_visit_order

                # Elimina el PowerupAgent de la grilla y el modelo
                self.model.grid.remove_agent(agent)
                self.model.schedule.remove(agent)
                print(f"[Debug] PowerupAgent eliminado de la posición {self.pos}")

                # Crea un RoadAgent con el número de orden de visita original
                road = RoadAgent(self.model.next_id(), self.model)
                road.visit_order = visit_order  # Asigna el número de orden original
                print(f"[Debug] Creando RoadAgent en la posición {self.pos} con número de orden {road.visit_order}")

                # Coloca el RoadAgent en la posición y en el scheduler
                self.model.grid.place_agent(road, self.pos)
                self.model.schedule.add(road)
                print(f"[Debug] RoadAgent con número de orden {road.visit_order} colocado en la posición {self.pos} exitosamente")

    def move_to_position(self, next_position):
        """
        Mueve a Bomberman a la posición indicada y marca el camino óptimo con
        un color amarillo si la posición es parte de dicho camino.
        
        Args:
            next_position: La posición a la que se moverá Bomberman.
        """
        from AgentArquitecture.road import RoadAgent

        if self.pos is None or next_position is None:
            print("Movimiento abortado: Bomberman ha sido eliminado o la siguiente posición no es válida.")
            return

        # Marca la posición actual como visitada si contiene un RoadAgent en el camino óptimo
        agents_in_current_cell = self.model.grid.get_cell_list_contents([self.pos])
        for agent in agents_in_current_cell:
            if isinstance(agent, RoadAgent) and self.pos in self.original_path:
                agent.is_visited = True  # Marca como visitado para cambiar el color en el camino óptimo

        # Mueve a Bomberman a la siguiente posición y recolecta cualquier comodín
        self.model.grid.move_agent(self, next_position)
        self.is_moving = True
        print(f"Moviéndose a la posición: {self.pos}")
        self.collect_powerup()

    def retreat_on_optimal_path(self):
        """
        Retrocede en el camino óptimo para evitar una explosión si Bomberman
        colocó una bomba y está esperando su detonación.
        """
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
        """
        Reanuda el camino óptimo después de que Bomberman ha retrocedido 
        debido a una explosión, asegurando que siga su trayectoria planificada.
        """
        if self.pos in self.original_path:
            current_index = self.original_path.index(self.pos)
            self.path_to_exit = self.original_path[current_index + 1:]

    def is_adjacent(self, pos1, pos2):
        """
        Verifica si dos posiciones son adyacentes en una cuadrícula.
        
        Args:
            pos1: Primer posición a verificar.
            pos2: Segunda posición a verificar.
        
        Returns:
            bool: True si las posiciones son adyacentes, False en caso contrario.
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

    def move_to_exit_or_safety(self):
        """
        Mueve a Bomberman hacia la salida o a un lugar seguro dependiendo de las condiciones
        en el camino, colocando una bomba si se encuentra un obstáculo y retrocediendo si
        está en espera de explosión.
        """
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
        """
        Ejecuta un paso en la simulación para Bomberman, actualizando su dirección, 
        moviéndose hacia la salida, y revisando si necesita colocar una bomba o retroceder.
        """
        if self.pos is None:
            return

        # Manejar riesgo de bomba
        if isinstance(self.search_strategy, AlphaBetaSearch) and self.model.state.bomb_risk(self.pos):
            safe_position = self.model.state.find_safe_position(self.pos)
            if safe_position:
                self.move_to_position(safe_position)
                return
        if self.pos is None:
            return

        # Si no se ha inicializado la búsqueda, configurarla
        if not self.is_search_initialized:
            start_position = (self.pos[0], self.pos[1])

            if isinstance(self.search_strategy, AlphaBetaSearch):
                # Ejecuta la búsqueda para alfa-beta
                game_state = GameState(self.model, is_bomberman_turn=True)
                best_action = self.search_strategy.run(
                    game_state=game_state,
                    depth=3,
                    is_bomberman_turn=True
                )

                # Realizar la acción calculada por alfa-beta
                if best_action == "place_bomb":
                    self.place_bomb()
                    return
                elif best_action and isinstance(best_action, tuple):
                    self.move_to_position(best_action)
                    return
            else:
                # Para otras estrategias (BFS, DFS, etc.), inicializar la búsqueda
                self.search_strategy.start_search(start_position, self.model.goal_position)
                self.is_search_initialized = True

        # Calcular dirección para avanzar
        self.direction = self.calculate_direction()

        # Explorar el laberinto según la estrategia (para BFS, DFS, A*, etc.)
        if not isinstance(self.search_strategy, AlphaBetaSearch):  # Evita llamar a explore_step en alfa-beta
            if not self.has_explored:
                self.search_strategy.explore_step(self)
                if self.has_explored:
                    print("Camino óptimo calculado:", self.path_to_exit)
                    self.original_path = self.path_to_exit[:]
                return

        # Moverse hacia la salida o ejecutar una estrategia defensiva
        self.move_to_exit_or_safety()
        print(f"Posición actual de Bomberman en este paso: {self.pos}") 