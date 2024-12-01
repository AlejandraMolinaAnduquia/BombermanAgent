from AgentArquitecture.globe import GlobeAgent
from AgentArquitecture.bomb import BombAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.metal import MetalAgent
from AgentArquitecture.rock import RockAgent
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
        Evalúa si una posición está en peligro debido a una bomba cercana.

        Args:
            pos (tuple): Coordenadas de la posición a evaluar.

        Returns:
            bool: True si la posición está en peligro, False en caso contrario.
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
        Verifica si una posición es válida para moverse (no contiene obstáculos).
        """
        
        if not (0 <= pos[0] < self.width and 0 <= pos[1] < self.height):
            return False
        cell_contents = self.grid.get_cell_list_contents([pos])
        return all(not isinstance(agent, (BombAgent, GlobeAgent, MetalAgent, RockAgent)) for agent in cell_contents)


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
        """Genera las posiciones válidas desde una posición dada."""
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        return [new_pos for dx, dy in directions if self.is_valid_move((new_pos := (pos[0] + dx, pos[1] + dy)))]

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
            # Generar movimientos válidos
            moves = self.generate_moves(self.bomberman_position)
            # Ordenar movimientos en función de su distancia a la salida
            moves = sorted(moves, key=lambda pos: self.manhattan_distance(pos, self.goal_position))

            for move in moves:
                child_state = self.clone()
                child_state.bomberman_position = move
                child_state.last_action = move
                child_state.visited_positions = self.visited_positions[-5:] + [move]
                children.append(child_state)

            # Solo permitir colocar bombas si es útil
            if self.can_place_bomb() and self.is_bomb_useful():
                bomb_state = self.clone()
                bomb_state.add_bomb(self.bomberman_position)
                bomb_state.last_action = "place_bomb"
                bomb_state.visited_positions = self.visited_positions[-5:] + [self.bomberman_position]
                children.append(bomb_state)
        else:
            for globe in self.globes:
                moves = self.generate_moves(globe["position"])
                # Ordenar movimientos en función de la distancia a Bomberman
                moves = sorted(moves, key=lambda pos: self.manhattan_distance(pos, self.bomberman_position))

                for move in moves:
                    child_state = self.clone()
                    for child_globe in child_state.globes:
                        if child_globe["agent"].unique_id == globe["agent"].unique_id:
                            child_globe["position"] = move
                            break
                    child_state.last_action = move
                    child_state.visited_positions = self.visited_positions[-5:] + [move]
                    children.append(child_state)
        return children


    def is_bomb_useful(self):
        """
        Determina si colocar una bomba es útil para Bomberman.
        Retorna True si hay globos o obstáculos estratégicos cerca.
        """
        for globe in self.globes:
            distance = self.manhattan_distance(self.bomberman_position, globe["position"])
            if distance <= 2:  # Rango de destrucción de la bomba
                return True
        return False

    def can_place_bomb(self):
        """
        Verifica si Bomberman puede colocar una bomba en su posición actual.

        Returns:
            bool: True si puede colocar una bomba, False en caso contrario.
        """
        if self.bomberman_position in [bomb["position"] for bomb in self.bombs]:
            return False
        return True

    def add_bomb(self, position):
        """Agrega una bomba al estado actual y la registra correctamente en el modelo."""
        bomb = BombAgent(self.model.next_id(), self.model, position, destruction_power=2)
        self.model.grid.place_agent(bomb, position)
        self.model.schedule.add(bomb)
        self.bombs.append({"agent": bomb, "position": position})

    def is_terminal(self):
        """
        Verifica si el estado actual es un estado terminal del juego.

        Returns:
            bool: True si el juego ha terminado, False en caso contrario.
        """
        if self.bomberman_position == self.goal_position:
            return True
        if not self.generate_moves(self.bomberman_position) and not self.can_place_bomb():
            return True
        if not self.globes:
            return True
        if any(globe["position"] == self.bomberman_position for globe in self.globes):
            return True
        return False

    def evaluate(self, is_bomberman_turn):
        if is_bomberman_turn:
            distance_to_goal = self.manhattan_distance(self.bomberman_position, self.goal_position)
            distance_to_globes = min(
                [self.manhattan_distance(self.bomberman_position, globe["position"]) for globe in self.globes],
                default=float('inf')
            )
            bomb_risk = self.bomb_risk(self.bomberman_position)

            # Penalización por bucles
            repetition_penalty = -50 if self.bomberman_position in self.visited_positions[-3:] else 0

            # Recompensa adicional por acercarse a la salida
            goal_proximity_reward = -distance_to_goal * 5

            return goal_proximity_reward + (10 / (distance_to_globes + 1)) - (100 if bomb_risk else 0) + repetition_penalty
        else:
            distance_to_bomberman = min(
                [self.manhattan_distance(globe["position"], self.bomberman_position) for globe in self.globes],
                default=float('inf')
            )
            bomberman_risk = self.bomb_risk(self.bomberman_position)

            # Penalización por movimientos repetitivos
            repetition_penalty = -20 if any(globe["position"] in self.visited_positions[-3:] for globe in self.globes) else 0

            # Recompensa por cercar a Bomberman
            encirclement_reward = -distance_to_bomberman * 5

            return encirclement_reward + (50 if bomberman_risk else 0) + repetition_penalty




