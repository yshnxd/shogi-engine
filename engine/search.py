"""Alpha-beta search with transposition table."""

import time
from typing import Tuple, Optional, Dict
from .board import Board, Move
from .eval import Evaluator


class TTEntry:
    """Transposition table entry."""
    EXACT = 0
    LOWER = 1
    UPPER = 2
    
    def __init__(self, depth: int, score: float, flag: int, move: Optional[Move] = None):
        self.depth = depth
        self.score = score
        self.flag = flag
        self.move = move


class Searcher:
    """Alpha-beta search engine."""
    
    def __init__(self, evaluator: Evaluator, max_tt_size: int = 100000):
        """Initialize searcher."""
        self.eval = evaluator
        self.tt: Dict[int, TTEntry] = {}
        self.max_tt_size = max_tt_size
        
        self.nodes_searched = 0
        self.tt_hits = 0
        self.beta_cutoffs = 0
    
    def search(self, board: Board, depth: int = 4, time_limit: float = 5.0) -> Tuple[Optional[Move], float]:
        """Find best move using iterative deepening."""
        self.nodes_searched = 0
        self.tt_hits = 0
        self.beta_cutoffs = 0
        self.tt = {}
        
        start_time = time.time()
        best_move = None
        best_score = float('-inf')
        
        for d in range(1, depth + 1):
            if time.time() - start_time > time_limit:
                break
            
            score, move = self._search(board, d)
            if move is not None:
                best_move = move
                best_score = score
        
        return best_move, best_score
    
    def _search(self, board: Board, depth: int) -> Tuple[float, Optional[Move]]:
        """Search with given depth."""
        side = board.side_to_move
        moves = board.generate_moves(side)
        
        if not moves:
            return float('-inf'), None
        
        best_move = moves[0]
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        for move in moves:
            new_board = board.make_move(move)
            score = -self._alpha_beta(new_board, depth - 1, -beta, -alpha)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, score)
        
        return best_score, best_move
    
    def _alpha_beta(self, board: Board, depth: int, alpha: float, beta: float) -> float:
        """Alpha-beta pruning recursion."""
        self.nodes_searched += 1
        
        if depth == 0:
            return self.eval.evaluate(board, board.side_to_move)
        
        moves = board.generate_moves(board.side_to_move)
        if not moves:
            return float('-inf')
        
        max_eval = float('-inf')
        
        for move in moves:
            new_board = board.make_move(move)
            eval_score = -self._alpha_beta(new_board, depth - 1, -beta, -alpha)
            
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            
            if alpha >= beta:
                self.beta_cutoffs += 1
                break
        
        return max_eval
    
    def _board_hash(self, board: Board) -> int:
        """Simple hash of board state."""
        hash_val = 0
        for sq in range(81):
            piece = board.squares[sq]
            if piece:
                piece_hash = (piece.type.value * 2 + piece.side) * 2 + (1 if piece.promoted else 0)
                hash_val ^= piece_hash * (sq + 1)
        
        hash_val ^= board.side_to_move
        return hash_val
