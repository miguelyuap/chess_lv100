"""Unit test script to verify AIEngine and GameState functionality."""

import chess
from engine.game_state import GameState
from engine.ai_engine import AIEngine

def test_engine():
    print("--- Running AI Engine Tests ---")
    game = GameState()
    ai = AIEngine()

    print("Initial Board Evaluation:", ai.evaluate_board(game.board))
    assert ai.evaluate_board(game.board) == 0, "Initial board eval should be 0"

    # Test Best Move at Level 10
    move_l10 = ai.get_best_move(game.board, level=10)
    print("Level 10 move:", move_l10)
    assert move_l10 in game.board.legal_moves, "AI move must be legal"

    # Test Best Move at Level 50
    move_l50 = ai.get_best_move(game.board, level=50)
    print("Level 50 move:", move_l50)
    assert move_l50 in game.board.legal_moves, "AI move must be legal"

    # Test Mate in 1 detection
    # Fool's mate setup: 1. f3 e5 2. g4 Qh4#
    game.reset()
    game.make_move(chess.Move.from_uci("f2f3"))
    game.make_move(chess.Move.from_uci("e7e5"))
    game.make_move(chess.Move.from_uci("g2g4"))

    # Black (AI) should immediately find Qh4# (e8h4)
    black_move = ai.get_best_move(game.board, level=80)
    print("Tactical Test - Black move in Fool's Mate setup:", black_move)
    assert black_move == chess.Move.from_uci("d8h4"), f"AI should find Mate in 1 (Qh4), found {black_move}"

    print("[SUCCESS] All AI Engine tests passed successfully!")

if __name__ == "__main__":
    test_engine()
