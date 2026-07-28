"""Piece rendering module for Chess Lv.100 application.

Handles piece asset loading and high-quality vector/font fallback rendering with surface caching.
"""

import os
from typing import Dict, Tuple, Optional
import pygame
import chess
from config import PIECE_UNICODE, SQUARE_SIZE


class PieceRenderer:
    """Manages piece visual representations with caching and fallback rendering."""

    def __init__(self, piece_size: int = SQUARE_SIZE, assets_dir: Optional[str] = None) -> None:
        """Initialize piece renderer.

        Args:
            piece_size: Size in pixels of piece square container.
            assets_dir: Path to directory containing custom piece PNG assets.
        """
        self.piece_size: int = piece_size
        self.assets_dir: str = assets_dir or os.path.join(os.path.dirname(__file__), "..", "assets", "pieces")
        self._surface_cache: Dict[str, pygame.Surface] = {}
        
        from config import get_font
        self.font: pygame.font.Font = get_font(int(self.piece_size * 0.72))

        # Pre-render piece surfaces
        self._build_cache()

    def _build_cache(self) -> None:
        """Loads assets from disk or generates fallback surfaces for all piece types."""
        symbols = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
        
        for symbol in symbols:
            filename = f"{'w' if symbol.isupper() else 'b'}{symbol.upper()}.png"
            filepath = os.path.join(self.assets_dir, filename)
            
            if os.path.exists(filepath):
                try:
                    surf = pygame.image.load(filepath).convert_alpha()
                    surf = pygame.transform.smoothscale(surf, (self.piece_size, self.piece_size))
                    self._surface_cache[symbol] = surf
                    continue
                except Exception:
                    pass  # Fallback to dynamic text/vector rendering
            
            # Dynamic styled fallback surface
            self._surface_cache[symbol] = self._create_fallback_surface(symbol)

    def _create_fallback_surface(self, symbol: str) -> pygame.Surface:
        """Creates an anti-aliased piece surface with subtle shadow effects for high aesthetic quality.

        Args:
            symbol: Piece character FEN representation (e.g. 'K', 'q', 'P').

        Returns:
            Pygame Surface with the rendered piece graphics.
        """
        surface = pygame.Surface((self.piece_size, self.piece_size), pygame.SRCALPHA)
        is_white = symbol.isupper()
        unicode_char = PIECE_UNICODE.get(symbol, symbol)

        # Main piece color scheme
        piece_color: Tuple[int, int, int] = (252, 252, 255) if is_white else (32, 34, 40)
        shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 110)
        outline_color: Tuple[int, int, int] = (40, 42, 48) if is_white else (220, 220, 230)

        # Render glyph shadow
        shadow_txt = self.font.render(unicode_char, True, shadow_color[:3])
        txt_rect = shadow_txt.get_rect(center=(self.piece_size // 2 + 2, self.piece_size // 2 + 3))
        surface.blit(shadow_txt, txt_rect)

        # Render main piece glyph
        main_txt = self.font.render(unicode_char, True, piece_color)
        main_rect = main_txt.get_rect(center=(self.piece_size // 2, self.piece_size // 2))
        
        # Additional contrast outline ring if needed
        if not is_white:
            # Draw slight outline for dark pieces for high clarity
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                out_txt = self.font.render(unicode_char, True, outline_color)
                surface.blit(out_txt, main_rect.move(dx, dy))

        surface.blit(main_txt, main_rect)
        return surface

    def get_piece_surface(self, piece: chess.Piece) -> pygame.Surface:
        """Retrieves the pre-rendered Surface for a chess.Piece.

        Args:
            piece: The python-chess Piece object.

        Returns:
            Cached Pygame Surface for rendering.
        """
        symbol = piece.symbol()
        if symbol not in self._surface_cache:
            self._surface_cache[symbol] = self._create_fallback_surface(symbol)
        return self._surface_cache[symbol]
