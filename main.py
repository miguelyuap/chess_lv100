"""Main entry point for Chess Lv.100 Pygame Application.

Integrates game loop, board GUI, 1-100 Level AI Engine (Minimax + Alpha-Beta),
and interactive UI widgets (difficulty slider, action buttons, AI status indicator).
"""

import sys
import os
import pygame
import chess

from typing import Optional, List, Tuple

# Ensure project root is in Python path for clean modular imports
sys.path.insert(0, os.path.dirname(__file__))

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BOARD_SIZE,
    PANEL_WIDTH,
    FPS,
    COLOR_BACKGROUND,
    COLOR_PANEL_BG,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT,
)
from engine.game_state import GameState
from engine.ai_engine import AIEngine
from gui.board_view import BoardView
from gui.ui_components import Slider, Button


class ChessApp:
    """Main application manager for Chess Lv.100."""

    def __init__(self) -> None:
        """Initialize Pygame display, game logic, AI engine, and UI components."""
        pygame.init()
        pygame.display.set_caption("Chess Lv.100 - Python Edition")

        from config import get_font

        try:
            # SCALED allows 1000x720 canvas to scale dynamically on mobile screens
            self.screen: pygame.Surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
        except Exception:
            self.screen: pygame.Surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True

        # Game State & Views
        self.game_state: GameState = GameState()
        self.board_view: BoardView = BoardView(self.game_state, x_offset=0, y_offset=0)
        self.ai_engine: AIEngine = AIEngine()

        # Match Configuration
        self.vs_ai: bool = True
        self.ai_color: chess.Color = chess.BLACK

        # Interactive UI Components (Positioned in side panel)
        panel_x = BOARD_SIZE + 24
        self.level_slider: Slider = Slider(
            x=panel_x,
            y=240,
            width=PANEL_WIDTH - 48,
            height=20,
            min_val=1,
            max_val=100,
            initial_val=50,
            label="Nivel de Dificultad IA"
        )

        self.btn_new_game: Button = Button(
            x=panel_x,
            y=300,
            width=PANEL_WIDTH - 48,
            height=36,
            text="Nueva Partida",
            callback=self._action_reset
        )

        self.btn_undo: Button = Button(
            x=panel_x,
            y=348,
            width=PANEL_WIDTH - 48,
            height=36,
            text="Deshacer Movimiento",
            callback=self._action_undo
        )

        self.btn_switch_side: Button = Button(
            x=panel_x,
            y=396,
            width=PANEL_WIDTH - 48,
            height=36,
            text="Cambiar Bando (Blancas/Negras)",
            callback=self._action_switch_side
        )

        self.btn_toggle_mode: Button = Button(
            x=panel_x,
            y=444,
            width=PANEL_WIDTH - 48,
            height=36,
            text="Modo: Humano vs IA",
            callback=self._action_toggle_mode
        )

        # Typography
        self.font_title: pygame.font.Font = get_font(24, bold=True)
        self.font_body: pygame.font.Font = get_font(15)
        self.font_small: pygame.font.Font = get_font(13)

        # Animation counter for thinking indicator
        self._anim_frame: int = 0

    def run(self) -> None:
        """Main application execution loop."""
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def _handle_events(self) -> None:
        """Processes user keyboard, mouse, and widget events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Delegate events to UI Widgets first
            self.level_slider.handle_event(event)
            self.btn_new_game.handle_event(event)
            self.btn_undo.handle_event(event)
            self.btn_switch_side.handle_event(event)
            self.btn_toggle_mode.handle_event(event)

            # Delegate mouse hover to board view
            if event.type == pygame.MOUSEMOTION:
                self.board_view.handle_mouse_hover(event.pos)

            # Handle board clicks (only if it's human turn and AI isn't thinking)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                is_human_turn = not self.vs_ai or (self.game_state.turn != self.ai_color)
                if is_human_turn and not self.ai_engine.is_thinking:
                    self.board_view.handle_click(event.pos)

            # Keyboard Shortcuts
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self._action_reset()
                elif event.key in (pygame.K_u, pygame.K_z):
                    self._action_undo()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def _update(self) -> None:
        """Updates game state and triggers AI moves asynchronously."""
        self._anim_frame = (self._anim_frame + 1) % 60

        # Check if AI needs to move
        if (
            self.vs_ai
            and self.game_state.turn == self.ai_color
            and not self.game_state.is_game_over()
            and not self.ai_engine.is_thinking
        ):
            level = self.level_slider.value
            self.ai_engine.get_best_move_async(
                self.game_state.board,
                level,
                self._on_ai_move_calculated
            )

    def _on_ai_move_calculated(self, move: Optional[chess.Move]) -> None:
        """Callback invoked when AI engine finishes calculating best move in background thread."""
        if move and move in self.game_state.board.legal_moves:
            self.game_state.make_move(move)
            self.board_view.selected_square = None
            self.board_view.legal_moves = []

    def _action_reset(self) -> None:
        """Resets the board position."""
        self.game_state.reset()
        self.board_view.selected_square = None
        self.board_view.legal_moves = []

    def _action_undo(self) -> None:
        """Undoes last move (or last two moves if playing against AI)."""
        if self.ai_engine.is_thinking:
            return

        self.game_state.undo_move()
        # In VS AI mode, undo human move as well if it's now human turn again
        if self.vs_ai and self.game_state.turn == self.ai_color:
            self.game_state.undo_move()

        self.board_view.selected_square = None
        self.board_view.legal_moves = []

    def _action_switch_side(self) -> None:
        """Toggles AI side between Black and White."""
        self.ai_color = chess.WHITE if self.ai_color == chess.BLACK else chess.BLACK
        side_str = "Blancas" if self.ai_color == chess.WHITE else "Negras"
        self._action_reset()

    def _action_toggle_mode(self) -> None:
        """Toggles game mode between Human vs AI and Human vs Human."""
        self.vs_ai = not self.vs_ai
        mode_text = "Modo: Humano vs IA" if self.vs_ai else "Modo: 2 Jugadores"
        self.btn_toggle_mode.text = mode_text
        self._action_reset()

    def _draw(self) -> None:
        """Renders current frame."""
        self.screen.fill(COLOR_BACKGROUND)

        # 1. Render Chessboard
        self.board_view.draw(self.screen)

        # 2. Render Side Panel
        self._draw_side_panel()

        pygame.display.flip()

    def _draw_side_panel(self) -> None:
        """Renders side control & information panel."""
        panel_x = BOARD_SIZE
        panel_rect = pygame.Rect(panel_x, 0, PANEL_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect)

        # Branding
        title_surf = self.font_title.render("CHESS Lv. 100", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(title_surf, (panel_x + 24, 25))

        sub_surf = self.font_small.render("Minimax + Poda Alfa-Beta", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub_surf, (panel_x + 24, 55))

        # Divider line
        pygame.draw.line(self.screen, (52, 56, 68), (panel_x + 24, 80), (WINDOW_WIDTH - 24, 80), 2)

        # Game Status & AI Thinking Indicator
        status_header = self.font_small.render("ESTADO DEL JUEGO", True, COLOR_ACCENT)
        self.screen.blit(status_header, (panel_x + 24, 98))

        if self.ai_engine.is_thinking:
            dots = "." * ((self._anim_frame // 15) % 4)
            status_text = f"IA Pensando (Nvl {self.level_slider.value}){dots}"
            status_color = (255, 205, 60)
        else:
            status_text = self.game_state.get_status_text()
            status_color = COLOR_TEXT_PRIMARY

        status_surf = self.font_body.render(status_text, True, status_color)
        self.screen.blit(status_surf, (panel_x + 24, 120))

        # Match Info / Stats
        ply_count = self.game_state.board.ply()
        move_num = (ply_count // 2) + 1
        ai_side_str = "Negras" if self.ai_color == chess.BLACK else "Blancas"
        info_str = f"Jugada: {move_num} | IA Juega: {ai_side_str if self.vs_ai else 'Desactivada'}"
        stats_surf = self.font_small.render(info_str, True, COLOR_TEXT_MUTED)
        self.screen.blit(stats_surf, (panel_x + 24, 150))

        # Divider line
        pygame.draw.line(self.screen, (52, 56, 68), (panel_x + 24, 185), (WINDOW_WIDTH - 24, 185), 1)

        # Draw UI Widgets
        self.level_slider.draw(self.screen)
        self.btn_new_game.draw(self.screen)
        self.btn_undo.draw(self.screen)
        self.btn_switch_side.draw(self.screen)
        self.btn_toggle_mode.draw(self.screen)

        # Footer shortcut hint
        hint_surf = self.font_small.render("Atajos: [R] Reiniciar | [Z] Deshacer", True, COLOR_TEXT_MUTED)
        self.screen.blit(hint_surf, (panel_x + 24, WINDOW_HEIGHT - 35))


if __name__ == "__main__":
    try:
        app = ChessApp()
        app.run()
    except Exception as e:
        import traceback
        traceback.print_exc()

