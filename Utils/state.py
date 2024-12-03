
from AgentArquitecture.globe import GlobeAgent
from AgentArquitecture.bomb import BombAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.metal import MetalAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.goal import GoalAgent
from mesa.space import MultiGrid


class GameState:
    """
    Clase que encapsula el estado del juego y proporciona métodos para evaluar
    posiciones, calcular riesgos y generar acciones para los agentes.
    """

    def __init__(self, model, is_bomberman_turn=True):
        """
        Inicializa el estado del juego con información sobre la grilla y los agentes.

        Args:
            model (MazeModel): Instancia del modelo que contiene la grilla y agentes.
            is_bomberman_turn (bool): True si es el turno de Bomberman, False para los globos.
        """
        self.model = model
        self.grid = model.grid
        self.width = model.grid.width
        self.height = model.grid.height
        self.bomberman_position = self._find_bomberman()
        self.globes = self._find_globes()
        self.bombs = self._find_bombs()
        self.goal_position = model.goal_position
        self.is_bomberman_turn = is_bomberman_turn
        self.visited_positions = []  # Historial de posiciones recientes para evitar bucles
        self.explored_paths_bomberman = self.explore_entire_map()

        self.explored_paths_globes = {
            globe["agent"]: self.explore_entire_map()
            for globe in self.globes
        }

    def _find_bomberman(self):
        """Encuentra la posición de Bomberman en la grilla."""
        from AgentArquitecture.bomberman import BombermanAgent
        for content, pos in self.grid.coord_iter():
            if any(isinstance(agent, BombermanAgent) for agent in content):
                return pos
        return None

    def _find_globes(self):
        """Encuentra las posiciones de todos los globos en la grilla."""
        globes = []
        for content, pos in self.grid.coord_iter():
            for agent in content:
                if isinstance(agent, GlobeAgent):
                    globes.append({"agent": agent, "position": pos})
        return globes

    def _find_bombs(self):
        """Encuentra las posiciones de todas las bombas activas en la grilla."""
        bombs = []
        for content, pos in self.grid.coord_iter():
            for agent in content:
                if isinstance(agent, BombAgent):
                    bombs.append({"agent": agent, "position": pos})
        return bombs

    def bomb_risk(self, pos):
        """
        Evalúa si una posición está en peligro debido a bombas activas.
        """
        for bomb in self.bombs:
            bomb_pos = bomb["position"]
            power = bomb["agent"].destruction_power
            for direction in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                for step in range(1, power + 1):
                    risk_pos = (bomb_pos[0] + direction[0] * step, bomb_pos[1] + direction[1] * step)
                    if pos == risk_pos:
                        return True
        return False



    def is_valid_move(self, pos):
        """
        Determina si un movimiento a una posición específica es válido, verificando
        los límites del mapa y la presencia de agentes permitidos en esa celda.
        
        Args:
            pos (tuple): Coordenadas de la posición a verificar.
        
        Returns:
            bool: `True` si el movimiento es válido, `False` en caso contrario.
        """
        from AgentArquitecture.bomberman import BombermanAgent
        x, y = pos
        # Verifica si la posición está dentro de los límites de la cuadrícula
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False

        # Obtiene los agentes en la celda
        agents_in_cell = self.grid.get_cell_list_contents([pos])

        # Permitir moverse a celdas que solo contienen caminos, meta o rocas
        return all(
            isinstance(agent, (BombermanAgent,RoadAgent, GoalAgent, RockAgent)) for agent in agents_in_cell
        )

    def evaluate_position(self, pos, agent_type):
        """
        Evalúa la calidad de una posición para un agente.

        Args:
            pos (tuple): Coordenadas de la posición a evaluar.
            agent_type (str): Tipo del agente ("Bomberman" o "Globe").

        Returns:
            float: Puntuación de la posición.
        """
        if agent_type == "Bomberman":
            distance_to_goal = self.manhattan_distance(pos, self.goal_position)
            risk = self.bomb_risk(pos)
            return -distance_to_goal - (100 if risk else 0)
        elif agent_type == "Globe":
            distance_to_bomberman = self.manhattan_distance(pos, self.bomberman_position)
            risk = self.bomb_risk(pos)
            return distance_to_bomberman - (100 if risk else 0)

    def manhattan_distance(self, pos1, pos2):
        """Calcula la distancia de Manhattan entre dos posiciones."""
        if pos1 is None or pos2 is None:
            return float('inf')  # Penalización alta si falta una posición
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def generate_moves(self, pos):
        if pos is None:
            return []  # Si la posición es None, no hay movimientos válidos
        
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Solo movimientos ortogonales
        valid_moves = []

        for dx, dy in directions:
            new_pos = (pos[0] + dx, pos[1] + dy)
            if self.is_valid_move(new_pos):
                valid_moves.append(new_pos)
        return valid_moves


    def find_optimized_path_to_goal(self):
        """
        Encuentra el camino más corto hacia la salida (R_s) usando BFS.
        Retorna una lista de posiciones que representan el camino desde la posición
        actual de Bomberman hasta la salida. Si no hay un camino válido, retorna None.
        """
        from queue import Queue

        if not self.bomberman_position or not self.goal_position:
            return None  # Si no hay posición inicial o meta, no hay camino

        # Inicialización de la búsqueda BFS
        queue = Queue()
        queue.put((self.bomberman_position, []))  # (posición actual, camino hasta ahora)
        visited = set()

        while not queue.empty():
            current_pos, path = queue.get()

            # Si ya visitamos esta posición, omitimos
            if current_pos in visited:
                continue
            visited.add(current_pos)

            # Si llegamos a la meta, devolvemos el camino
            if current_pos == self.goal_position:
                return path + [current_pos]

            # Generar movimientos válidos desde la posición actual
            for move in self.generate_moves(current_pos):
                if move not in visited:
                    queue.put((move, path + [current_pos]))

        # Si no se encuentra un camino, retornar None
        return None



    def clone(self):
        """Crea una copia del estado actual."""
        clone_state = GameState(self.model, is_bomberman_turn=self.is_bomberman_turn)
        clone_state.bomberman_position = self.bomberman_position
        clone_state.globes = [{"agent": globe["agent"], "position": globe["position"]} for globe in self.globes]
        clone_state.bombs = [{"agent": bomb["agent"], "position": bomb["position"]} for bomb in self.bombs]
        return clone_state

    def get_children(self):
        children = []

        if self.is_bomberman_turn:
            # Generar movimientos para Bomberman
            moves = self.generate_moves(self.bomberman_position)
            for move in moves:
                child_state = self.clone()
                child_state.bomberman_position = move
                child_state.last_action = move
                children.append(child_state)

            # Generar acción de colocar bomba
            if self.can_place_bomb() and self.is_bomb_useful():
                bomb_state = self.clone()
                bomb_state.add_bomb(self.bomberman_position)
                bomb_state.last_action = "place_bomb"
                children.append(bomb_state)
        else:
            # Movimientos para los globos
            for globe in self.globes:
                moves = self.generate_moves(globe["position"])
                for move in moves:
                    child_state = self.clone()
                    for child_globe in child_state.globes:
                        if child_globe["agent"] == globe["agent"]:
                            child_globe["position"] = move
                            break
                    child_state.last_action = move
                    children.append(child_state)

                # Acción especial: ataque al estar a un paso de Bomberman
                if self.manhattan_distance(globe["position"], self.bomberman_position) == 1:
                    attack_state = self.clone()
                    attack_state.bomberman_position = None  # Bomberman eliminado
                    for child_globe in attack_state.globes:
                        if child_globe["agent"] == globe["agent"]:
                            child_globe["position"] = self.bomberman_position  # Globo ocupa la posición de Bomberman
                            break
                    attack_state.last_action = "attack"
                    children.append(attack_state)

        return children


    def is_terminal(self):
        # Actualizar posiciones antes de evaluar
        self.update_positions()

        # Si Bomberman ha sido eliminado, finalizar el juego
        if self.bomberman_position is None:
            print("[Fin de Juego] Bomberman ha sido eliminado.")
            self.model.running = False  # Detener la simulación
            return True  # Estado terminal

        # Verificar si algún globo puede atacar a Bomberman
        for globe in self.globes:
            if self.manhattan_distance(globe["position"], self.bomberman_position) == 1:
                # Eliminar a Bomberman y obtener su última posición
                last_bomberman_position = self.remove_bomberman_and_update_model()

                if last_bomberman_position is not None:
                    # Ajustar la posición según el mapa invertido
                    adjusted_position = last_bomberman_position
                    print(f"[Actualización] Globo movido de {globe['position']} a {adjusted_position} tras eliminar a Bomberman")
                    
                    # Actualizar la posición del globo
                    globe["position"] = adjusted_position
                    self.grid.move_agent(globe["agent"], adjusted_position)
                    
                    # Sincronizar el modelo y la interfaz
                    self.update_positions()
                    self.sync_with_interface()
                else:
                    print("[Error] No se pudo obtener la última posición de Bomberman")
                return True

        # Verificar si Bomberman llegó a la meta
        if self.bomberman_position == self.goal_position:
            print("[Fin de Juego] Bomberman alcanzó la meta.")
            self.model.running = False  # Detener la simulación
            return True

        # Verificar si Bomberman no puede moverse ni colocar bombas
        if not self.generate_moves(self.bomberman_position) and not self.can_place_bomb():
            print("[Fin de Juego] Bomberman no tiene movimientos válidos ni puede colocar bombas.")
            self.model.running = False  # Detener la simulación
            return True

        return False

    def sync_with_interface(self):
        """
        Fuerza la actualización del modelo con la interfaz gráfica.
        """
        self.update_positions()
        print(f"[Sincronización] Posiciones sincronizadas: Bomberman={self.bomberman_position}, Globos={[globe['position'] for globe in self.globes]}")


    def update_positions(self):
        """
        Actualiza las posiciones de Bomberman y los globos en tiempo real,
        asegurando precisión en los cálculos.
        """
        self.bomberman_position = self._find_bomberman()
        self.globes = self._find_globes()
        print(f"[Seguimiento] Posición actual de Bomberman: {self.bomberman_position}")
        print(f"[Seguimiento] Posiciones actuales de los globos: {[globe['position'] for globe in self.globes]}")



    def remove_bomberman_and_update_model(self):
        """
        Elimina a Bomberman del mapa y retorna su última posición.
        """
        if self.bomberman_position is not None:
            bomberman_last_position = self.bomberman_position
            agents_in_cell = self.grid.get_cell_list_contents([self.bomberman_position])
            for agent in agents_in_cell:
                from AgentArquitecture.bomberman import BombermanAgent
                if isinstance(agent, BombermanAgent):
                    self.grid.remove_agent(agent)
                    self.model.schedule.remove(agent)
                    print(f"[Actualización] Bomberman eliminado de {self.bomberman_position}")
                    break

            # Actualizar el estado del modelo
            self.bomberman_position = None
            self.update_positions()
            return bomberman_last_position
        return None



    def is_bomb_useful(self):
        """
        Determina si colocar una bomba es útil.
        """
        x, y = self.bomberman_position
        neighbors = [
            (x + dx, y + dy)
            for dx, dy in [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Prioridad de movimiento]
            if 0 <= x + dx < self.width and 0 <= y + dy < self.height
        ]
        for neighbor in neighbors:
            agents_in_cell = self.grid.get_cell_list_contents([neighbor])
            if any(isinstance(agent, (GlobeAgent, RockAgent)) for agent in agents_in_cell):
                return True
        return False


    def can_place_bomb(self):
        """
        Verifica si Bomberman puede colocar una bomba.
        Returns True si no hay bombas activas, False en caso contrario.
        """
        return not any(
            bomb["position"] == self.bomberman_position for bomb in self.bombs
        )



    def add_bomb(self, position):
        """Agrega una bomba con el poder de destrucción inicial de Bomberman."""
        destruction_power = 1  # Cambiar a 1 como valor inicial
        bomb = BombAgent(self.model.next_id(), self.model, position, destruction_power=destruction_power)
        self.model.grid.place_agent(bomb, position)
        self.model.schedule.add(bomb)
        self.bombs.append({"agent": bomb, "position": position})


    
    def find_safe_position(self, current_pos):
        """
        Encuentra una posición segura adyacente a la posición actual,
        evitando el alcance de explosiones.
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Movimientos ortogonales
        safe_positions = [
            (current_pos[0] + dx, current_pos[1] + dy)
            for dx, dy in directions
            if self.is_valid_move((current_pos[0] + dx, current_pos[1] + dy))
            and not self.bomb_risk((current_pos[0] + dx, current_pos[1] + dy))
        ]
        return safe_positions[0] if safe_positions else None



    def evaluate(self, is_bomberman_turn):
        if is_bomberman_turn:
            # Penalizar por estar en riesgo de bombas
            bomb_penalty = -500 if self.bomb_risk(self.bomberman_position) else 0
            
            # Priorizar la meta
            goal_reward = -self.manhattan_distance(self.bomberman_position, self.goal_position) * 100

            # Penalizar la proximidad de globos peligrosos
            globe_penalty = -300 if any(
                self.manhattan_distance(self.bomberman_position, globe["position"]) <= 2 for globe in self.globes
            ) else 0

            return goal_reward + bomb_penalty + globe_penalty
        else:
            # Globos intentan acercarse a Bomberman
            bomberman_penalty = -self.manhattan_distance(self.globes[0]["position"], self.bomberman_position) * 50

            # Evitar bombas
            bomb_penalty = -500 if self.bomb_risk(self.globes[0]["position"]) else 0

            return bomberman_penalty + bomb_penalty


    def rocks_in_path_to_goal(self):
        """
        Identifica las rocas en el camino hacia la meta usando un recorrido válido.
        """
        path_to_goal = self.find_path_to_goal(self.bomberman_position, self.goal_position)
        return [
            pos for pos in path_to_goal
            if any(isinstance(agent, RockAgent) for agent in self.grid.get_cell_list_contents([pos]))
        ]


    def find_path_to_goal(self, start_pos, goal_pos):
        """
        Encuentra un camino desde la posición de inicio hasta la meta usando BFS.
        Considera rocas como posiciones válidas si Bomberman puede destruirlas.
        """
        from queue import Queue

        visited = set()
        queue = Queue()
        queue.put((start_pos, []))  # (posición actual, camino hasta ahora)

        while not queue.empty():
            current_pos, path = queue.get()
            if current_pos in visited:
                continue

            visited.add(current_pos)
            if current_pos == goal_pos:
                return path + [goal_pos]

            # Generar movimientos válidos
            for move in self.generate_moves(current_pos):
                if move not in visited:
                    queue.put((move, path + [move]))

        # Si no hay camino, retorna lista vacía
        return []


    def explore_entire_map(self):
        """
        Explora el mapa completo y retorna todos los caminos posibles desde la posición inicial
        de cada agente relevante (Bomberman o Globos).
        
        Returns:
            dict: Un diccionario con los caminos explorados para Bomberman y los Globos.
        """
        from queue import Queue

        explored_paths = {"bomberman": {}, "globes": []}

        # Explorar el mapa para Bomberman
        start_pos = self.bomberman_position
        if start_pos:
            visited = set()
            queue = Queue()
            queue.put((start_pos, []))  # (posición actual, camino acumulado)

            while not queue.empty():
                current_pos, path = queue.get()
                if current_pos in visited:
                    continue

                visited.add(current_pos)
                explored_paths["bomberman"][current_pos] = path

                for move in self.generate_moves(current_pos):
                    if move not in visited:
                        queue.put((move, path + [move]))

        # Explorar el mapa para cada Globo
        for globe in self.globes:
            globe_start_pos = globe["position"]
            if globe_start_pos:
                visited = set()
                queue = Queue()
                queue.put((globe_start_pos, []))  # (posición actual, camino acumulado)

                globe_paths = {}
                while not queue.empty():
                    current_pos, path = queue.get()
                    if current_pos in visited:
                        continue

                    visited.add(current_pos)
                    globe_paths[current_pos] = path

                    for move in self.generate_moves(current_pos):
                        if move not in visited:
                            queue.put((move, path + [move]))

                explored_paths["globes"].append(globe_paths)

        return explored_paths