"""Performance benchmarking utilities."""

import time
import logging
from .board import Board
from .engine import ShogiEngine
from .eval import Evaluator


logger = logging.getLogger(__name__)


def benchmark_movegen(num_moves: int = 1000) -> float:
    """Benchmark move generation speed."""
    board = Board()
    start = time.time()
    
    for _ in range(num_moves):
        moves = board.generate_moves()
        if moves:
            board = board.make_move(moves[0])
    
    elapsed = time.time() - start
    mps = num_moves / elapsed if elapsed > 0 else 0
    logger.info(f"Move generation: {mps:.0f} moves/sec")
    return mps


def benchmark_eval(num_evals: int = 1000) -> float:
    """Benchmark evaluation speed."""
    board = Board()
    eval_fn = Evaluator()
    start = time.time()
    
    for _ in range(num_evals):
        eval_fn.evaluate(board, 0)
    
    elapsed = time.time() - start
    eps = num_evals / elapsed if elapsed > 0 else 0
    logger.info(f"Evaluation: {eps:.0f} evals/sec")
    return eps


def benchmark_search(depth: int = 4, time_limit: float = 5.0) -> float:
    """Benchmark search speed."""
    board = Board()
    engine = ShogiEngine(depth, time_limit)
    
    start = time.time()
    move = engine.get_best_move(board)
    elapsed = time.time() - start
    
    stats = engine.get_stats()
    nps = stats['nodes_searched'] / elapsed if elapsed > 0 else 0
    logger.info(f"Search: {nps:.0f} nodes/sec, {stats['nodes_searched']} nodes, {elapsed:.2f}s")
    return nps


def run_all_benchmarks():
    """Run all benchmarks."""
    logging.basicConfig(level=logging.INFO)
    
    print("\n=== Shogi Engine Benchmarks ===")
    print("\nMove Generation:")
    benchmark_movegen()
    
    print("\nEvaluation:")
    benchmark_eval()
    
    print("\nSearch (depth=4):")
    benchmark_search(depth=4, time_limit=5.0)


if __name__ == "__main__":
    run_all_benchmarks()
