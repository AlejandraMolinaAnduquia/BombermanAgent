
from AgentArquitecture.road import RoadAgent
from mesa import Agent
import random

class GlobeAgent(Agent):
    def __init__(self, unique_id, model):
        """
        Inicializa el agente GlobeAgent, que representa un globo enemigo en el juego.

        Args:
            unique_id: Identificador único del agente.
            model: El modelo de simulación al que pertenece el agente.
        """
        super().__init__(unique_id, model)
        self.awaiting_step_confirmation = False  # Marca si el agente está esperando confirmación de movimiento
        self.previous_visit_order = None  # Almacena el número de orden si está sobre una casilla numerada
        self.visit_order = None  # Número de orden asignado a las casillas en camino óptimo
        self.is_visited = False  # Indica si la casilla ha sido visitada

    def step(self):
        """
        Ejecuta un paso en la simulación para el Globo.
        """
        if self.pos is None:
            print(f"[Error] Globo {self.unique_id} no tiene posición.")
            return

        # Manejar riesgo de bomba
        if self.model.state.bomb_risk(self.pos):
            safe_position = self.model.state.find_safe_position(self.pos)
            if safe_position:
                print(f"[Globo {self.unique_id}] En peligro de bomba. Moviéndose a posición segura: {safe_position}")
                self.model.grid.move_agent(self, safe_position)
                return

        # Calcular el camino hacia Bomberman
        path_to_bomberman = self.calculate_path_to_bomberman()

        if path_to_bomberman:
            # Moverse al siguiente paso en el camino calculado
            next_step = path_to_bomberman[0]
            if self.should_wait_or_alternate(next_step):
                # Esperar o buscar un camino alternativo
                self.random_move()  # Intentar un movimiento aleatorio temporal
            else:
                print(f"[Globo {self.unique_id}] Moviéndose hacia Bomberman: {next_step}")
                self.model.grid.move_agent(self, next_step)

                # Si alcanza a Bomberman, manejar colisión
                if self.check_collision(self.get_bomberman_agent().pos):
                    self.handle_collision(self.get_bomberman_agent())
        else:
            print(f"[Globo {self.unique_id}] No encontró un camino hacia Bomberman. Moviéndose aleatoriamente.")
            self.random_move()



    def calculate_path_to_bomberman(self):
        """
        Calcula el camino óptimo hacia Bomberman, asegurándose de evitar colisiones con otros globos
        y siguiendo las heurísticas definidas.

        Returns:
            list: Lista de posiciones que representan el camino óptimo hacia Bomberman.
        """
        from queue import Queue

        if not self.pos or not self.get_bomberman_agent() or not self.get_bomberman_agent().pos:
            return []  # Si no hay posición o Bomberman, no se calcula un camino

        start_pos = self.pos
        bomberman_pos = self.get_bomberman_agent().pos
        visited = set()
        queue = Queue()
        queue.put((start_pos, []))  # (posición actual, camino acumulado)

        while not queue.empty():
            current_pos, path = queue.get()

            if current_pos in visited:
                continue
            visited.add(current_pos)

            # Si llegamos a Bomberman, retornamos el camino
            if current_pos == bomberman_pos:
                return path + [current_pos]

            # Generar movimientos válidos desde la posición actual
            for move in self.model.state.generate_moves(current_pos):
                # Evitar posiciones ocupadas por otros globos
                occupied_positions = {globe["position"] for globe in self.model.state.globes if globe["agent"] != self}
                if move in visited or move in occupied_positions:
                    continue
                queue.put((move, path + [move]))

        return []  # Si no se encuentra un camino, retorna lista vacía


    def should_wait_or_alternate(self, next_pos):
        """
        Verifica si el globo debe esperar o buscar un camino alternativo debido a otros globos.

        Args:
            next_pos (tuple): La posición a la que el globo quiere moverse.

        Returns:
            bool: True si debe esperar, False si puede proceder.
        """
        # Obtener las posiciones de los otros globos
        other_globe_positions = {globe["position"] for globe in self.model.state.globes if globe["agent"] != self}

        # Verificar si la posición siguiente está ocupada por otro globo
        if next_pos in other_globe_positions:
            print(f"[Globo {self.unique_id}] Esperando o alternando camino debido a bloqueo en {next_pos}.")
            return True
        return False


    def generate_moves(self, pos):
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Prioridad de movimiento
        valid_moves = []
        for dx, dy in directions:
            new_pos = (pos[0] + dx, pos[1] + dy)
            if self.is_valid_move(new_pos):
                valid_moves.append(new_pos)
        return valid_moves


    def random_move(self):
        """
        Ejecuta un paso de simulación para el globo. Intenta moverse en una dirección aleatoria
        y maneja las colisiones con Bomberman.
        """
        if self.pos is None:
            return  # Sale si el globo ha sido eliminado de la grilla

        bomberman = self.get_bomberman_agent()
        if bomberman is None or bomberman.pos is None:
            return  # Sale si Bomberman no está en la simulación o su posición no es válida

        # Comprueba si hay colisión o colisión cruzada con Bomberman
        if self.awaiting_step_confirmation:
            if self.check_collision(bomberman.pos) or self.check_cross_collision(self.pos, bomberman):
                self.handle_collision(bomberman)
                return 
            self.awaiting_step_confirmation = False

        if bomberman.is_moving:
            # Define las direcciones posibles y las mezcla para elegir una aleatoria
            possible_directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Prioridad de movimiento
            random.shuffle(possible_directions)

            moved = False  # Controla si el globo logra moverse
            for direction in possible_directions:
                new_position = (self.pos[0] + direction[0], self.pos[1] + direction[1])

                # Verifica si la nueva posición está dentro de los límites y vacía
                if not self.model.grid.out_of_bounds(new_position) and self.model.is_cell_empty(new_position):
                    # Recupera los agentes en la posición actual para verificar si es un camino
                    current_cell_agents = self.model.grid.get_cell_list_contents([self.pos])
                    for agent in current_cell_agents:
                        if isinstance(agent, RoadAgent):
                            # Guarda el número de orden de visita del camino actual
                            self.previous_visit_order = agent.visit_order

                    # Crea un camino en la posición actual del globo, antes de moverse
                    road = RoadAgent(self.model.next_id(), self.model)
                    road.visit_order = self.previous_visit_order  # Mantiene el número de orden si lo tenía
                    self.model.grid.place_agent(road, self.pos)

                    # Mueve el globo a la nueva posición
                    self.model.grid.move_agent(self, new_position)
                    self.awaiting_step_confirmation = True
                    moved = True
                    break

            if not moved:
                print("No se pudo mover el globo a ninguna nueva posición")


    def handle_collision(self, bomberman):
        """
        Maneja la colisión con Bomberman. Elimina a Bomberman y detiene la simulación.

        Args:
            bomberman: La instancia de BombermanAgent con la que el globo ha colisionado.
        """
        collision_position = bomberman.pos
        self.model.grid.remove_agent(bomberman)  # Elimina Bomberman de la grilla
        self.model.schedule.remove(bomberman)  # Elimina Bomberman del scheduler
        self.model.running = False  # Detiene la simulación
        print(f"Colisión detectada entre GlobeAgent y BombermanAgent en la posición {collision_position}. Bomberman eliminado y simulación finalizada.")

    def get_bomberman_agent(self):
        """
        Busca y retorna la instancia de BombermanAgent en la simulación.

        Returns:
            bomberman: El agente Bomberman si está en el scheduler; de lo contrario, None.
        """
        from AgentArquitecture.bomberman import BombermanAgent
        for agent in self.model.schedule.agents:
            if isinstance(agent, BombermanAgent):
                return agent
        return None

    def check_collision(self, bomberman_position):
        """
        Verifica si Bomberman y el globo están en la misma posición.

        Args:
            bomberman_position: La posición actual de Bomberman.

        Returns:
            bool: True si hay colisión, False de lo contrario.
        """
        x, y = self.pos
        bx, by = bomberman_position
        return abs(x - bx) + abs(y - by) == 0  # Evalúa si están en la misma posición

    def check_cross_collision(self, current_position, bomberman):
        """
        Verifica si se producirá una colisión cruzada entre el globo y Bomberman, considerando su siguiente movimiento.

        Args:
            current_position: La posición actual del globo.
            bomberman: La instancia de BombermanAgent.

        Returns:
            bool: True si hay colisión cruzada, False de lo contrario.
        """
        bx, by = bomberman.pos 
        next_bomberman_position = (bx + bomberman.direction[0], by + bomberman.direction[1])
        return current_position == next_bomberman_position  # Devuelve True si Bomberman y el globo se cruzan