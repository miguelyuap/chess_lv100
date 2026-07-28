"""Configuration module for Chess Lv.100 application.

Defines global constants for screen metrics, color schemes, font settings,
and game behavior rules.
"""

from typing import Tuple
import pygame

# Screen and UI Dimensions
BOARD_SIZE: int = 720
SQUARE_SIZE: int = BOARD_SIZE // 8  # 90 px per square
PANEL_WIDTH: int = 280
WINDOW_WIDTH: int = BOARD_SIZE + PANEL_WIDTH  # 1000 px
WINDOW_HEIGHT: int = BOARD_SIZE  # 720 px
FPS: int = 60

# Color Palette (Modern Dark / Slate-Wood Aesthetic)
COLOR_LIGHT_SQUARE: Tuple[int, int, int] = (238, 238, 210)   # Warm Ivory
COLOR_DARK_SQUARE: Tuple[int, int, int] = (118, 150, 86)     # Elegant Chess Green
COLOR_BACKGROUND: Tuple[int, int, int] = (24, 25, 29)         # Rich Dark Charcoal
COLOR_PANEL_BG: Tuple[int, int, int] = (33, 35, 42)          # Surface Slate

# Highlights & Indicators (RGBA format for alpha blending)
COLOR_SELECT_HIGHLIGHT: Tuple[int, int, int, int] = (255, 205, 60, 160)   # Radiant Gold
COLOR_LAST_MOVE_LIGHT: Tuple[int, int, int, int] = (205, 210, 106, 170)   # Soft Olive Gold
COLOR_LAST_MOVE_DARK: Tuple[int, int, int, int] = (170, 185, 80, 170)
COLOR_LEGAL_DOT: Tuple[int, int, int, int] = (20, 20, 20, 80)             # Translucent Shadow Dot
COLOR_LEGAL_CAPTURE: Tuple[int, int, int, int] = (220, 53, 69, 140)       # Translucent Red Ring
COLOR_HOVER: Tuple[int, int, int, int] = (255, 255, 255, 40)              # Subtle White Glow

# Typography & Text Colors
COLOR_TEXT_PRIMARY: Tuple[int, int, int] = (240, 240, 245)
COLOR_TEXT_MUTED: Tuple[int, int, int] = (140, 145, 160)
COLOR_ACCENT: Tuple[int, int, int] = (74, 144, 226)

# Chess Piece FEN Symbol Map
PIECE_UNICODE: dict[str, str] = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Safely retrieves a font compatible across Windows, Linux, Android, and Web."""
    import pygame
    pygame.font.init()
    try:
        font_path = pygame.font.match_font("dejavusans") or pygame.font.match_font("sans")
        if font_path:
            f = pygame.font.Font(font_path, size)
            f.set_bold(bold)
            return f
    except Exception:
        pass
    f = pygame.font.Font(None, size)
    f.set_bold(bold)
    return f

