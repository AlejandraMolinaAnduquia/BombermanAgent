class AlphaBetaSearch:
    def __init__(self, max_depth):
        self.max_depth = max_depth

    def evaluate_state(self, state, is_bomberman_turn):
        if state.is_terminal():
            if state.bomberman_position is None:
                return float('-inf')  # Penalización máxima: Bomberman eliminado
            if state.bomberman_position == state.goal_position:
                return float('inf')  # Recompensa máxima: Bomberman llegó a la meta

        if is_bomberman_turn:
            # Evaluación para Bomberman
            bomb_penalty = 500 if state.bomb_risk(state.bomberman_position) else 0
            distance_to_goal = state.manhattan_distance(state.bomberman_position, state.goal_position)
            goal_reward = -distance_to_goal * 100
            globe_penalty = -300 if any(
                state.manhattan_distance(state.bomberman_position, globe["position"]) <= 1
                for globe in state.globes
            ) else 0
            return goal_reward - bomb_penalty + globe_penalty
        else:
            # Evaluación independiente para cada globo
            total_score = 0
            for globe in state.globes:
                distance_to_bomberman = state.manhattan_distance(globe["position"], state.bomberman_position)
                total_score -= distance_to_bomberman * 50  # Penalizar la distancia a Bomberman
            return total_score

    def alpha_beta(self, state, depth, alpha, beta, maximizing_player):
        if depth == 0 or state.is_terminal():
            print(f"Evaluando estado terminal: Bomberman: {state.bomberman_position}, Globos: {[g['position'] for g in state.globes]}")
            return self.evaluate_state(state, maximizing_player)

        if maximizing_player:
            max_eval = float('-inf')
            for child in state.get_children():
                eval = self.alpha_beta(child, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for child in state.get_children():
                eval = self.alpha_beta(child, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def run(self, game_state, depth, is_bomberman_turn):
        """
        Ejecuta el algoritmo de búsqueda Alfa-Beta. Prioriza la salida sobre cualquier otra acción.
        """
        # Priorizar el camino a la salida para Bomberman
        if is_bomberman_turn:
            path_to_goal = game_state.find_optimized_path_to_goal()
            if path_to_goal:
                print(f"[Alfa-Beta] Bomberman prioriza camino a la salida: {path_to_goal}")
                return path_to_goal[0]  # Retorna el siguiente paso hacia la salida

        best_action = None
        best_value = float('-inf') if is_bomberman_turn else float('inf')

        for child in game_state.get_children():
            value = self.alpha_beta(
                state=child,
                depth=depth - 1,
                alpha=float('-inf'),
                beta=float('inf'),
                maximizing_player=not is_bomberman_turn
            )

            if (is_bomberman_turn and value > best_value) or (not is_bomberman_turn and value < best_value):
                best_value = value
                best_action = child.last_action

        return best_action