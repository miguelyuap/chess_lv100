"""Board view module for Pygame Chess interface.

Renders the 8x8 chessboard, handles mouse selection, highlights legal moves,
and draws pieces cleanly using python-chess as the backend engine.
"""

from typing import Optional, List, Tuple
import pygame
import chess

from config import (
    BOARD_SIZE,
    SQUARE_SIZE,
    COLOR_LIGHT_SQUARE,
    COLOR_DARK_SQUARE,
    COLOR_SELECT_HIGHLIGHT,
    COLOR_LAST_MOVE_LIGHT,
    COLOR_LAST_MOVE_DARK,
    COLOR_LEGAL_DOT,
    COLOR_LEGAL_CAPTURE,
    COLOR_HOVER,
    COLOR_TEXT_MUTED,
    COLOR_PANEL_BG
)
from engine.game_state import GameState
from gui.piece_renderer import PieceRenderer


class BoardView:
    """Handles visual rendering of the chess board, square selection, and user click interaction."""

    def __init__(self, game_state: GameState, x_offset: int = 0, y_offset: int = 0) -> None:
        """Initialize the BoardView.

        Args:
            game_state: Reference to the active GameState instance.
            x_offset: Horizontal pixel offset for board positioning.
            y_offset: Vertical pixel offset for board positioning.
        """
        self.game_state: GameState = game_state
        self.x_offset: int = x_offset
        self.y_offset: int = y_offset
        self.renderer: PieceRenderer = PieceRenderer(SQUARE_SIZE)

        # Selection and interaction state
        self.selected_square: Optional[int] = None
        self.legal_moves: List[chess.Move] = []
        self.hovered_square: Optional[int] = None

        from config import get_font
        self.font_notation: pygame.font.Font = get_font(13, bold=True)

    def square_to_screen_coords(self, square: int) -> Tuple[int, int]:
        """Converts a python-chess square index (0-63) to screen pixel coordinates (x, y)."""
        file_idx = chess.square_file(square)
        rank_idx = chess.square_rank(square)
        col = file_idx
        row = 7 - rank_idx
        return self.x_offset + col * SQUARE_SIZE, self.y_offset + row * SQUARE_SIZE

    def screen_coords_to_square(self, pos: Tuple[int, int]) -> Optional[int]:
        """Converts screen pixel position (x, y) to python-chess square index (0-63)."""
        x, y = pos
        rel_x = x - self.x_offset
        rel_y = y - self.y_offset

        if 0 <= rel_x < BOARD_SIZE and 0 <= rel_y < BOARD_SIZE:
            col = rel_x // SQUARE_SIZE
            row = rel_y // SQUARE_SIZE
            file_idx = col
            rank_idx = 7 - row
            return chess.square(file_idx, rank_idx)
        return None

    def handle_mouse_hover(self, pos: Tuple[int, int]) -> None:
        """Updates hovered square index based on mouse cursor coordinates."""
        self.hovered_square = self.screen_coords_to_square(pos)

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Handles a mouse click event on the board.

        Args:
            pos: Mouse position tuple (x, y).

        Returns:
            True if a move was executed, False otherwise.
        """
        clicked_sq = self.screen_coords_to_square(pos)
        if clicked_sq is None:
            self.selected_square = None
            self.legal_moves = []
            return False

        # If a square was already selected
        if self.selected_square is not None:
            # Look for legal move targeting clicked square
            matching_move = None
            for move in self.legal_moves:
                if move.to_square == clicked_sq:
                    matching_move = move
                    break

            if matching_move:
                # Handle pawn promotion (default to queen for rapid UX)
                piece = self.game_state.get_piece_at(self.selected_square)
                if piece and piece.piece_type == chess.PAWN:
                    to_rank = chess.square_rank(clicked_sq)
                    if to_rank in (0, 7):
                        matching_move.promotion = chess.QUEEN

                # Execute move
                move_executed = self.game_state.make_move(matching_move)
                self.selected_square = None
                self.legal_moves = []
                return move_executed

        # Select a new square if it contains a piece of the active player
        piece_at_click = self.game_state.get_piece_at(clicked_sq)
        if piece_at_click and piece_at_click.color == self.game_state.turn:
            self.selected_square = clicked_sq
            self.legal_moves = self.game_state.get_legal_moves_for_square(clicked_sq)
        else:
            self.selected_square = None
            self.legal_moves = []

        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Renders the entire chessboard, highlights, pieces, and notations.

        Args:
            surface: Pygame target surface for rendering.
        """
        self._draw_squares(surface)
        self._draw_highlights(surface)
        self._draw_legal_move_indicators(surface)
        self._draw_pieces(surface)
        self._draw_notation(surface)

    def _draw_squares(self, surface: pygame.Surface) -> None:
        """Draws the 8x8 alternating light and dark board squares."""
        for row in range(8):
            for col in range(8):
                is_light = (row + col) % 2 == 0
                color = COLOR_LIGHT_SQUARE if is_light else COLOR_DARK_SQUARE
                rect = pygame.Rect(
                    self.x_offset + col * SQUARE_SIZE,
                    self.y_offset + row * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE
                )
                pygame.draw.rect(surface, color, rect)

    def _draw_highlights(self, surface: pygame.Surface) -> None:
        """Draws highlights for last move, selection, and mouse hover."""
        overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

        # Highlight last executed move
        last_move = self.game_state.last_move
        if last_move:
            for sq in (last_move.from_square, last_move.to_square):
                row = 7 - chess.square_rank(sq)
                col = chess.square_file(sq)
                is_light = (row + col) % 2 == 0
                color = COLOR_LAST_MOVE_LIGHT if is_light else COLOR_LAST_MOVE_DARK
                overlay.fill(color)
                surface.blit(overlay, self.square_to_screen_coords(sq))

        # Highlight currently selected square
        if self.selected_square is not None:
            overlay.fill(COLOR_SELECT_HIGHLIGHT)
            surface.blit(overlay, self.square_to_screen_coords(self.selected_square))

        # Highlight hovered square if not selected
        if self.hovered_square is not None and self.hovered_square != self.selected_square:
            overlay.fill(COLOR_HOVER)
            surface.blit(overlay, self.square_to_screen_coords(self.hovered_square))

    def _draw_legal_move_indicators(self, surface: pygame.Surface) -> None:
        """Renders subtle translucent dots or capture rings on destination squares."""
        if not self.legal_moves:
            return

        indicator_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        center = (SQUARE_SIZE // 2, SQUARE_SIZE // 2)

        for move in self.legal_moves:
            dest_sq = move.to_square
            dest_pos = self.square_to_screen_coords(dest_sq)
            indicator_surface.fill((0, 0, 0, 0))

            is_capture = self.game_state.board.is_capture(move)
            if is_capture:
                # Draw translucent red capture ring around square edge
                pygame.draw.circle(indicator_surface, COLOR_LEGAL_CAPTURE, center, SQUARE_SIZE // 2 - 4, width=5)
            else:
                # Draw subtle dot in center
                pygame.draw.circle(indicator_surface, COLOR_LEGAL_DOT, center, SQUARE_SIZE // 6)

            surface.blit(indicator_surface, dest_pos)

    def _draw_pieces(self, surface: pygame.Surface) -> None:
        """Renders pieces from python-chess board onto their corresponding squares."""
        board = self.game_state.board
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                pos = self.square_to_screen_coords(square)
                piece_surf = self.renderer.get_piece_surface(piece)
                surface.blit(piece_surf, pos)

    def _draw_notation(self, surface: pygame.Surface) -> None:
        """Renders file labels (a-h) and rank labels (1-8) along board edges."""
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['8', '7', '6', '5', '4', '3', '2', '1']

        for i in range(8):
            # File notation (a-h) on bottom row
            is_light_file = (7 + i) % 2 == 0
            color_file = COLOR_DARK_SQUARE if is_light_file else COLOR_LIGHT_SQUARE
            txt_file = self.font_notation.render(files[i], True, color_file)
            surface.blit(txt_file, (self.x_offset + i * SQUARE_SIZE + SQUARE_SIZE - 14, self.y_offset + 7 * SQUARE_SIZE + SQUARE_SIZE - 18))

            # Rank notation (1-8) on left column
            is_light_rank = (i + 0) % 2 == 0
            color_rank = COLOR_DARK_SQUARE if is_light_rank else COLOR_LIGHT_SQUARE
            txt_rank = self.font_notation.render(ranks[i], True, color_rank)
            surface.blit(txt_rank, (self.x_offset + 5, self.y_offset + i * SQUARE_SIZE + 4))
