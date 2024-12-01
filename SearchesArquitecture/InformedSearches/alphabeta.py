class AlphaBetaSearch:
    def __init__(self, max_depth):
        """
        Inicializa la clase para la poda alfa-beta.

        Args:
            max_depth (int): La profundidad máxima para analizar el árbol de búsqueda.
        """
        self.max_depth = max_depth

    def evaluate_state(self, state, is_bomberman_turn):
        """
        Evalúa un estado del juego.

        Args:
            state (GameState): Estado actual del juego.
            is_bomberman_turn (bool): True si es el turno de Bomberman, False si es el turno de los globos.

        Returns:
            float: Valor heurístico del estado.
        """
        return state.evaluate(is_bomberman_turn)

    def alpha_beta(self, state, depth, alpha, beta, maximizing_player):
        # Detectar bucles explícitamente
        if state.visited_positions.count(state.bomberman_position) > 3:
            return float('-inf') if maximizing_player else float('inf')

        if depth == 0 or state.is_terminal():
            return state.evaluate(maximizing_player)

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

        for child in game_state.get_children():
            value = self.alpha_beta(
                state=child,
                depth=depth - 1,
                alpha=float('-inf'),
                beta=float('inf'),
                maximizing_player=not is_bomberman_turn
            )
            print(f"Evaluando acción {child.last_action} con valor {value}")  # Depuración
            if is_bomberman_turn:
                if value > best_value:
                    best_value = value
                    best_action = child.last_action
            else:
                if value < best_value:
                    best_value = value
                    best_action = child.last_action

        print(f"Mejor acción seleccionada: {best_action} con valor {best_value}")
        return best_action

