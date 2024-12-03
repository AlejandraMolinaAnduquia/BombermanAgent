class AlphaBetaSearch:
    def __init__(self, max_depth):
        self.max_depth = max_depth

    def evaluate_state(self, state, is_bomberman_turn):
        if is_bomberman_turn:
            # Penalización por riesgo de bomba
            bomb_penalty = 500 if state.bomb_risk(state.bomberman_position) else 0

            # Prioridad máxima hacia la meta
            distance_to_goal = state.manhattan_distance(state.bomberman_position, state.goal_position)
            goal_reward = -distance_to_goal * 100

            # Penalización por proximidad a globos peligrosos
            globe_penalty = -300 if any(
                state.manhattan_distance(state.bomberman_position, globe["position"]) <= 2
                for globe in state.globes
            ) else 0

            return goal_reward - bomb_penalty + globe_penalty
        else:
            # Globos intentan acercarse a Bomberman
            if state.globes:
                distance_to_bomberman = min(
                    state.manhattan_distance(globe["position"], state.bomberman_position)
                    for globe in state.globes
                )
                return -distance_to_bomberman * 100
            return 0  # Sin globos, no penalizar



    def alpha_beta(self, state, depth, alpha, beta, maximizing_player):
        if depth == 0 or state.is_terminal():
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
        best_action = None
        best_value = float('-inf') if is_bomberman_turn else float('inf')

        # Verificar riesgo actual
        current_position = (
            game_state.bomberman_position if is_bomberman_turn else game_state.globes[0]["position"]
        )
        if game_state.bomb_risk(current_position):
            safe_position = game_state.find_safe_position(current_position)
            if safe_position:
                return safe_position

        # Continuar con Alpha-Beta Search
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
