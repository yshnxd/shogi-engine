"""Evaluation function for Shogi positions."""

from typing import Dict
from .board import Board, PieceType


class Evaluator:
    """Evaluates Shogi positions using linear features."""
    
    def __init__(self):
        """Initialize with default weights."""
        self._init_piece_values()
        self._init_feature_weights()
    
    def _init_piece_values(self):
        """Initialize material values."""
        self.piece_values = {
            PieceType.PAWN: 1,
            PieceType.LANCE: 3,
            PieceType.KNIGHT: 3,
            PieceType.SILVER: 5,
            PieceType.GOLD: 6,
            PieceType.BISHOP: 8,
            PieceType.ROOK: 8,
            PieceType.KING: 0,
        }
        
        self.promoted_bonuses = {
            PieceType.PAWN: 4,
            PieceType.LANCE: 3,
            PieceType.KNIGHT: 3,
            PieceType.SILVER: 1,
            PieceType.BISHOP: 2,
            PieceType.ROOK: 2,
        }
    
    def _init_feature_weights(self):
        """Initialize feature weights."""
        self.w_mobility = 5
        self.w_king_safety = 10
        self.w_hand = 1.0
    
    def evaluate(self, board: Board, side: int = 0) -> float:
        """Evaluate position from perspective of given side."""
        score = 0.0
        
        # Material
        for sq in range(81):
            piece = board.squares[sq]
            if piece is None:
                continue
            
            val = self.piece_values[piece.type]
            if piece.promoted:
                val += self.promoted_bonuses.get(piece.type, 0)
            
            if piece.side == 0:
                score -= val
            else:
                score += val
        
        # Hand pieces
        for piece_type in PieceType:
            black_hand = board.hand[0][piece_type]
            white_hand = board.hand[1][piece_type]
            hand_val = self.piece_values[piece_type] * self.w_hand
            score += (white_hand - black_hand) * hand_val
        
        # Return from perspective of requested side
        if side == 0:
            return -score
        return score
