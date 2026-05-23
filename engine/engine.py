"""Main engine coordinator."""

import logging
from typing import Optional, Tuple
from .board import Board, Move
from .eval import Evaluator
from .search import Searcher
from .learner import Learner, GameRecorder


logger = logging.getLogger(__name__)


class ShogiEngine:
    """Main Shogi engine."""
    
    def __init__(self, search_depth: int = 4, time_per_move: float = 5.0):
        """Initialize engine."""
        self.eval = Evaluator()
        self.searcher = Searcher(self.eval)
        self.learner = Learner(self.eval)
        self.game_recorder = GameRecorder()
        
        self.search_depth = search_depth
        self.time_per_move = time_per_move
    
    def get_best_move(self, board: Board) -> Optional[Move]:
        """Get best move for current position."""
        move, score = self.searcher.search(board, self.search_depth, self.time_per_move)
        if move:
            logger.info(f"Best move: {move}, score: {score:.2f}")
        return move
    
    def play_self_game(self, max_moves: int = 300) -> Tuple[int, int]:
        """Play a self-play game."""
        board = Board()
        move_count = 0
        
        while move_count < max_moves:
            moves = board.generate_moves()
            if not moves:
                if board.side_to_move == 0:
                    return (0, 1)
                else:
                    return (1, 0)
            
            move = self.get_best_move(board)
            if move is None:
                move = moves[0]
            
            self.game_recorder.record_move(board, move)
            board = board.make_move(move)
            move_count += 1
        
        return (0, 0)
    
    def train(self, num_games: int = 10, learning_rate: float = 0.01):
        """Train engine via self-play."""
        self.learner.learning_rate = learning_rate
        
        for game_num in range(num_games):
            logger.info(f"\n=== Self-play game {game_num + 1}/{num_games} ===")
            
            black_wins, white_wins = self.play_self_game()
            if black_wins:
                outcome = 0
            elif white_wins:
                outcome = 1
            else:
                outcome = 0
            
            self.game_recorder.finalize_game(outcome)
            
            games = self.game_recorder.get_games()
            if games:
                last_game = games[-1]
                self.learner.learn_from_game(last_game['moves'], last_game['outcome'])
    
    def get_stats(self):
        """Return search statistics."""
        return {
            'nodes_searched': self.searcher.nodes_searched,
            'tt_hits': self.searcher.tt_hits,
            'beta_cutoffs': self.searcher.beta_cutoffs,
            'tt_size': len(self.searcher.tt),
        }
