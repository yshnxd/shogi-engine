"""Board representation and move generation for Shogi.

Uses an 81-bit integer for the board and simple list-based piece tracking.
For efficiency, we could upgrade to rotated bitboards later.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Set
from enum import Enum


class PieceType(Enum):
    """Shogi piece types."""
    PAWN = 0
    LANCE = 1
    KNIGHT = 2
    SILVER = 3
    GOLD = 4
    BISHOP = 5
    ROOK = 6
    KING = 7


class Piece:
    """Represents a piece on the board."""
    
    def __init__(self, piece_type: PieceType, side: int, promoted: bool = False):
        self.type = piece_type
        self.side = side  # 0 = black, 1 = white
        self.promoted = promoted
    
    def __repr__(self):
        prefix = "+" if self.promoted else ""
        side_str = "B" if self.side == 0 else "W"
        return f"{prefix}{self.type.name[0]}{side_str}"
    
    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return (self.type == other.type and 
                self.side == other.side and 
                self.promoted == other.promoted)


@dataclass
class Move:
    """Represents a move (either a piece move or drop)."""
    from_sq: Optional[int]  # None for drops
    to_sq: int
    promotion: bool = False
    capture: bool = False
    drop_piece: Optional[PieceType] = None  # Set for drops
    
    def __repr__(self):
        from_str = self._sq_to_notation(self.from_sq) if self.from_sq is not None else "drop"
        to_str = self._sq_to_notation(self.to_sq)
        promo = "=+" if self.promotion else ""
        return f"{from_str}{to_str}{promo}"
    
    @staticmethod
    def _sq_to_notation(sq: int) -> str:
        """Convert square index (0-80) to notation (1a-9i)."""
        file = sq % 9 + 1
        rank = sq // 9 + 1
        rank_char = chr(ord('a') + rank - 1)
        return f"{file}{rank_char}"


class Board:
    """Shogi board with pieces and hand holdings.
    
    Layout:
      0  1  2  3  4  5  6  7  8
      9 10 11 12 13 14 15 16 17
     18 19 20 21 22 23 24 25 26
     27 28 29 30 31 32 33 34 35
     36 37 38 39 40 41 42 43 44
     45 46 47 48 49 50 51 52 53
     54 55 56 57 58 59 60 61 62
     63 64 65 66 67 68 69 70 71
     72 73 74 75 76 77 78 79 80
    
    Promotion zone for black: ranks 7-9 (squares 54-80)
    Promotion zone for white: ranks 1-3 (squares 0-26)
    """
    
    # Promotion zones
    BLACK_PROMOTION_ZONE = set(range(54, 81))  # Ranks 7-9
    WHITE_PROMOTION_ZONE = set(range(0, 27))   # Ranks 1-3
    
    def __init__(self):
        """Initialize board in starting position."""
        self.squares = [None] * 81  # squares[i] = Piece or None
        self.hand = [self._init_hand(), self._init_hand()]  # Captured pieces
        self.side_to_move = 0  # 0 = black, 1 = white
        self._init_starting_position()
    
    def _init_hand(self):
        """Initialize empty hand holdings."""
        return {pt: 0 for pt in PieceType}
    
    def _init_starting_position(self):
        """Set up pieces in starting Shogi position."""
        # Black (side 0) in ranks 1-3 (indices 0-26)
        # White (side 1) in ranks 7-9 (indices 54-80)
        
        # Black back rank (index 0-8)
        self.squares[0] = Piece(PieceType.ROOK, 0)
        self.squares[1] = Piece(PieceType.BISHOP, 0)
        self.squares[2] = Piece(PieceType.GOLD, 0)
        self.squares[3] = Piece(PieceType.SILVER, 0)
        self.squares[4] = Piece(PieceType.KING, 0)
        self.squares[5] = Piece(PieceType.SILVER, 0)
        self.squares[6] = Piece(PieceType.GOLD, 0)
        self.squares[7] = Piece(PieceType.BISHOP, 0)
        self.squares[8] = Piece(PieceType.ROOK, 0)
        
        # Black pawns (index 9-17)
        for i in range(9, 18):
            self.squares[i] = Piece(PieceType.PAWN, 0)
        
        # White back rank (index 72-80)
        self.squares[80] = Piece(PieceType.ROOK, 1)
        self.squares[79] = Piece(PieceType.BISHOP, 1)
        self.squares[78] = Piece(PieceType.GOLD, 1)
        self.squares[77] = Piece(PieceType.SILVER, 1)
        self.squares[76] = Piece(PieceType.KING, 1)
        self.squares[75] = Piece(PieceType.SILVER, 1)
        self.squares[74] = Piece(PieceType.GOLD, 1)
        self.squares[73] = Piece(PieceType.BISHOP, 1)
        self.squares[72] = Piece(PieceType.ROOK, 1)
        
        # White pawns (index 63-71)
        for i in range(63, 72):
            self.squares[i] = Piece(PieceType.PAWN, 1)
    
    def copy(self) -> 'Board':
        """Return a deep copy of the board."""
        new_board = Board.__new__(Board)
        new_board.squares = [p if p is None else Piece(p.type, p.side, p.promoted) for p in self.squares]
        new_board.hand = [
            {pt: count for pt, count in self.hand[0].items()},
            {pt: count for pt, count in self.hand[1].items()}
        ]
        new_board.side_to_move = self.side_to_move
        return new_board
    
    def is_valid_square(self, sq: int) -> bool:
        """Check if square index is on the board (0-80)."""
        return 0 <= sq < 81
    
    def is_empty(self, sq: int) -> bool:
        """Check if square is empty."""
        return self.squares[sq] is None
    
    def generate_moves(self, side: Optional[int] = None) -> List[Move]:
        """Generate all legal moves for a side."""
        if side is None:
            side = self.side_to_move
        
        moves = []
        
        # Regular piece moves (simplified - king only for now)
        for sq in range(81):
            piece = self.squares[sq]
            if piece is None or piece.side != side:
                continue
            
            # Simple king moves as placeholder
            if piece.type == PieceType.KING:
                for delta in [-10, -9, -8, -1, 1, 8, 9, 10]:
                    to_sq = sq + delta
                    if self.is_valid_square(to_sq):
                        if self.is_empty(to_sq):
                            moves.append(Move(sq, to_sq))
        
        return moves if moves else [Move(sq, sq)]  # Return dummy move if no moves
    
    def make_move(self, move: Move) -> 'Board':
        """Apply a move and return the new board state."""
        new_board = self.copy()
        
        if move.from_sq == move.to_sq:
            new_board.side_to_move = 1 - new_board.side_to_move
            return new_board
        
        if move.drop_piece is not None:
            new_board.squares[move.to_sq] = Piece(move.drop_piece, new_board.side_to_move)
            new_board.hand[new_board.side_to_move][move.drop_piece] -= 1
        else:
            piece = new_board.squares[move.from_sq]
            if move.capture:
                captured_piece = new_board.squares[move.to_sq]
                new_board.hand[new_board.side_to_move][captured_piece.type] += 1
            
            if move.promotion and piece:
                piece.promoted = True
            
            new_board.squares[move.to_sq] = piece
            new_board.squares[move.from_sq] = None
        
        new_board.side_to_move = 1 - new_board.side_to_move
        return new_board
    
    def __repr__(self) -> str:
        """Pretty-print the board."""
        lines = []
        lines.append("  9 8 7 6 5 4 3 2 1")
        for rank in range(9):
            line = chr(ord('a') + rank) + " "
            for file in range(9, 0, -1):
                sq = rank * 9 + (file - 1)
                piece = self.squares[sq]
                if piece is None:
                    line += ". "
                else:
                    symbol = piece.type.name[0]
                    if piece.promoted:
                        symbol = "+" + symbol
                    symbol += ("B" if piece.side == 0 else "W")
                    line += symbol + " "
            lines.append(line)
        return "\n".join(lines)
