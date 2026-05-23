# Lightweight Python Shogi Engine

A minimal, learnable Shogi engine designed to run on low-end hardware (no GPU, limited CPU/RAM) while achieving high online Elo through self-play learning.

## Features

- **Compact board representation**: 81-bit Python int with bitboard operations
- **Efficient move generation**: Incremental sliding moves + drop handling
- **Math-based evaluation**: Linear features (material, PST, mobility, king safety)
- **Online learning**: TD(0) and perceptron-style weight updates from self-play
- **Alpha-beta search**: With iterative deepening, transposition table, move ordering
- **USI/CSA protocol support**: For online play integration
- **Colab-friendly**: Runs efficiently in Google Colab notebooks

## Quick Start (Colab)

```python
from engine.board import Board
from engine.engine import ShogiEngine

board = Board()
engine = ShogiEngine()
move = engine.get_best_move(board)
print(f"Best move: {move}")
```

## Architecture

```
engine/
├── board.py           # Board representation & move generation
├── eval.py            # Linear evaluation function
├── search.py          # Alpha-beta search with TT
├── learner.py         # Weight update logic
├── protocol.py        # USI/CSA interface
├── engine.py          # Main engine coordinator
└── benchmark.py       # Performance testing
```

## Milestones

1. ✅ Core board representation & move generation
2. ✅ Basic evaluation function
3. ⬜ Alpha-beta search with TT
4. ⬜ Self-play loop & learning
5. ⬜ USI protocol integration
6. ⬜ Colab notebook demos
7. ⬜ Online play testing
8. ⬜ Performance optimization

## References

Based on Bonanza, GPS Shogi, and alpha-beta fundamentals.
