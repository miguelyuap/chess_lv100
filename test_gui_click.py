"""Automated test for GUI click & move indicators."""

import pygame
import chess
from engine.game_state import GameState
from gui.board_view import BoardView

def test_click_and_draw():
    pygame.init()
    surface = pygame.Surface((800, 800))
    game = GameState()
    view = BoardView(game, 0, 0)

    # Click E2 Pawn (square e2 = 12 in python-chess)
    e2_sq = chess.E2
    e2_pos = view.square_to_screen_coords(e2_sq)
    # Add offset to click inside square center
    click_pos = (e2_pos[0] + 10, e2_pos[1] + 10)

    move_made = view.handle_click(click_pos)
    assert not move_made, "First click selects piece, does not make move"
    assert view.selected_square == chess.E2, "E2 square should be selected"
    assert len(view.legal_moves) == 2, "E2 pawn has 2 legal moves (E3, E4)"

    # Test drawing legal move indicators (should not raise any AttributeError)
    view.draw(surface)

    # Click E4 destination square (e4 = 28)
    e4_sq = chess.E4
    e4_pos = view.square_to_screen_coords(e4_sq)
    click_e4 = (e4_pos[0] + 10, e4_pos[1] + 10)

    move_made = view.handle_click(click_e4)
    assert move_made, "Clicking legal destination square E4 should execute move"
    assert view.selected_square is None, "Selection should clear after move"
    assert game.board.piece_at(chess.E4).symbol() == 'P', "Pawn should be on E4"

    print("[SUCCESS] GUI click and legal move indicators drawing test passed!")

if __name__ == "__main__":
    test_click_and_draw()
