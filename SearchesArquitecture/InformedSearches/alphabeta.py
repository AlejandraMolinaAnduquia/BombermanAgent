class AlphaBetaSearch:
    # Clase que implementa el algoritmo de búsqueda Alfa-Beta para evaluar estados del juego.

    def __init__(self, max_depth):
        # Inicializa el algoritmo con una profundidad máxima.
        self.max_depth = max_depth
        self.cont_poda = 0 ##

    def evaluate_state(self, state, is_bomberman_turn):
        # Evalúa el estado actual del juego en función de si es el turno de Bomberman o de los globos.
        
        if state.is_terminal():
            # Si el estado es terminal (el juego ha terminado)...
            if state.bomberman_position is None:
                # Si Bomberman fue eliminado, retorna la penalización máxima (-∞).
                return float('-inf')
            if state.bomberman_position == state.goal_position:
                # Si Bomberman alcanzó la meta, retorna la recompensa máxima (+∞).
                return float('inf')

        if is_bomberman_turn:
            # Si es el turno de Bomberman, evalúa desde su perspectiva.
            
            bomb_penalty = 500 if state.bomb_risk(state.bomberman_position) else 0
            # Penaliza si Bomberman está en riesgo de una explosión de bomba.
            
            distance_to_goal = state.manhattan_distance(state.bomberman_position, state.goal_position)
            # Calcula la distancia Manhattan entre Bomberman y la meta.
            
            goal_reward = -distance_to_goal * 100
            # Asigna una recompensa negativa proporcional a la distancia a la meta.
            
            globe_penalty = -300 if any(
                state.manhattan_distance(state.bomberman_position, globe["position"]) <= 1
                for globe in state.globes
            ) else 0
            # Penaliza si algún globo está a distancia 1 de Bomberman.
            
            return goal_reward - bomb_penalty + globe_penalty
            # Retorna la evaluación combinada para Bomberman.
        
        else:
            # Si no es el turno de Bomberman, evalúa desde la perspectiva de los globos.
            
            total_score = 0
            # Inicializa la puntuación total de los globos.
            
            for globe in state.globes:
                # Itera sobre todos los globos en el estado actual.
                
                distance_to_bomberman = state.manhattan_distance(globe["position"], state.bomberman_position)
                # Calcula la distancia de cada globo a Bomberman.
                
                total_score -= distance_to_bomberman * 50
                # Penaliza la distancia de los globos a Bomberman (los globos intentan acercarse).
            
            return total_score
            # Retorna la evaluación combinada para los globos.

    def alpha_beta(self, state, depth, alpha, beta, maximizing_player):
        # Implementa el algoritmo de búsqueda Alfa-Beta recursivo.
        print("podando")
        if depth == 0 or state.is_terminal():
            # Si se alcanza la profundidad máxima o el estado es terminal...
            
            print(f"Evaluando estado terminal: Bomberman: {state.bomberman_position}, Globos: {[g['position'] for g in state.globes]}")
            # Imprime información del estado terminal.
            
            return self.evaluate_state(state, maximizing_player)
            # Evalúa y retorna el puntaje del estado actual.

        if maximizing_player:
            # Si es el turno del jugador maximizador (Bomberman)...
            
            max_eval = float('-inf')
            # Inicializa el valor máximo como -∞.
            
            for child in state.get_children():
                # Itera sobre los posibles estados hijos.
                
                eval = self.alpha_beta(child, depth - 1, alpha, beta, False)
                # Llama recursivamente al algoritmo para evaluar el estado hijo.
                
                max_eval = max(max_eval, eval)
                # Actualiza el valor máximo encontrado.
                
                alpha = max(alpha, eval)
                # Actualiza el límite alfa.
                
                if beta <= alpha:
                    # Si beta es menor o igual a alfa, se realiza el podado.
                    
                    self.cont_poda += 1
                    break
            
            return max_eval
            # Retorna el valor máximo encontrado.

        else:
            # Si es el turno del jugador minimizador (globos)...
            
            min_eval = float('inf')
            # Inicializa el valor mínimo como +∞.
            
            for child in state.get_children():
                # Itera sobre los posibles estados hijos.
                
                eval = self.alpha_beta(child, depth - 1, alpha, beta, True)
                # Llama recursivamente al algoritmo para evaluar el estado hijo.
                
                min_eval = min(min_eval, eval)
                
                # Actualiza el valor mínimo encontrado.
                
                beta = min(beta, eval)
                # Actualiza el límite beta.
                
                if beta <= alpha:
                    self.cont_poda += 1
                    #print("cantidad de nodos podados",self.cont_poda)
                    # Si beta es menor o igual a alfa, se realiza el podado.
                    break
            
            return min_eval
            # Retorna el valor mínimo encontrado.

    def run(self, game_state, depth, is_bomberman_turn):
        """
        Ejecuta el algoritmo de búsqueda Alfa-Beta para un estado inicial.
        Prioriza el camino a la meta para Bomberman sobre cualquier otra acción.
        """
        
        best_action = None
        # Inicializa la mejor acción como `None`.
        
        best_value = float('-inf') if is_bomberman_turn else float('inf')
        # Define el valor inicial según si es el turno de Bomberman (maximizador) o los globos (minimizador).

        for child in game_state.get_children():
        
            # Itera sobre los posibles estados hijos.
            
            value = self.alpha_beta(
                state=child,
                depth=depth - 1,
                alpha=float('-inf'),
                beta=float('inf'),
                maximizing_player=not is_bomberman_turn
            )
            # Evalúa el estado hijo usando Alfa-Beta.

            if (is_bomberman_turn and value > best_value) or (not is_bomberman_turn and value < best_value):
                # Actualiza la mejor acción basada en el valor evaluado.
                best_value = value
                best_action = child.last_action
        print("cantidad de nodos podados",self.cont_poda)
        return best_action
        # Retorna la mejor acción calculada.
