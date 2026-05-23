"""Learning and weight update logic."""

from typing import List, Tuple
from .board import Board, Move, PieceType
from .eval import Evaluator


class Learner:
    """Online learning from self-play games."""
    
    def __init__(self, evaluator: Evaluator, learning_rate: float = 0.01):
        """Initialize learner."""
        self.eval = evaluator
        self.learning_rate = learning_rate
        self.regularization = 0.001
    
    def learn_from_game(self, game_moves: List[Tuple[Board, Move, int]], final_outcome: int):
        """Update weights from a game."""
        for board, move, side in game_moves:
            v_before = self.eval.evaluate(board, side)
            board_after = board.make_move(move)
            v_after = self.eval.evaluate(board_after, side)
            
            if (side == 0 and final_outcome == 0) or (side == 1 and final_outcome == 1):
                target = 1.0
            elif (side == 0 and final_outcome == 1) or (side == 1 and final_outcome == 0):
                target = 0.0
            else:
                target = 0.5
            
            td_error = target - v_before
            self._update_weights_td(board, td_error)
    
    def _update_weights_td(self, board: Board, td_error: float):
        """TD-based weight update."""
        eta = self.learning_rate * td_error
        
        for piece_type in PieceType:
            black_count = sum(1 for sq in range(81) 
                            if board.squares[sq] and board.squares[sq].type == piece_type and board.squares[sq].side == 0)
            white_count = sum(1 for sq in range(81) 
                            if board.squares[sq] and board.squares[sq].type == piece_type and board.squares[sq].side == 1)
            
            delta = eta * (white_count - black_count)
            self.eval.piece_values[piece_type] += delta
            self.eval.piece_values[piece_type] *= (1 - self.regularization)


class GameRecorder:
    """Records games for learning."""
    
    def __init__(self):
        self.games: List[Tuple[List, int]] = []
    
    def record_move(self, board: Board, move: Move):
        """Record a move."""
        if not self.games or 'moves' not in self.games[-1]:
            self.games.append({'moves': [], 'start_board': board.copy()})
        
        self.games[-1]['moves'].append((board.copy(), move, board.side_to_move))
    
    def finalize_game(self, outcome: int):
        """Mark game as complete."""
        if self.games:
            self.games[-1]['outcome'] = outcome
    
    def get_games(self):
        """Retrieve recorded games."""
        return self.games
