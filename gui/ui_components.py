"""UI components module for Chess Lv.100 application.

Provides interactive sliders, buttons, and mode switches styled for the Pygame interface.
"""

from typing import Tuple, Callable, Optional
import pygame

from config import (
    COLOR_ACCENT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_PANEL_BG
)


class Slider:
    """Interactive horizontal slider widget for numerical selection (e.g. Difficulty Level 1-100)."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        min_val: int = 1,
        max_val: int = 100,
        initial_val: int = 50,
        label: str = "Nivel de IA"
    ) -> None:
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.min_val: int = min_val
        self.max_val: int = max_val
        self.value: int = initial_val
        self.label: str = label
        self.dragging: bool = False

        # Visual styling
        self.track_height: int = 6
        self.thumb_radius: int = 10
        self.track_color: Tuple[int, int, int] = (60, 64, 76)
        self.fill_color: Tuple[int, int, int] = COLOR_ACCENT
        self.thumb_color: Tuple[int, int, int] = (250, 250, 255)

        from config import get_font
        self.font: pygame.font.Font = get_font(14, bold=True)
        self.font_val: pygame.font.Font = get_font(14, bold=True)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handles mouse interactions with slider track and thumb.

        Returns:
            True if the slider value changed, False otherwise.
        """
        changed = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check thumb or track click
            mouse_pos = event.pos
            thumb_x = self._get_thumb_x()
            thumb_rect = pygame.Rect(thumb_x - self.thumb_radius, self.rect.y - self.thumb_radius, self.thumb_radius * 2, self.thumb_radius * 2 + self.rect.height)

            if self.rect.collidepoint(mouse_pos) or thumb_rect.collidepoint(mouse_pos):
                self.dragging = True
                changed = self._update_val_from_x(mouse_pos[0])

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            changed = self._update_val_from_x(event.pos[0])

        return changed

    def _get_thumb_x(self) -> int:
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + ratio * self.rect.width)

    def _update_val_from_x(self, mouse_x: int) -> bool:
        rel_x = max(0, min(mouse_x - self.rect.x, self.rect.width))
        ratio = rel_x / self.rect.width
        new_val = int(round(self.min_val + ratio * (self.max_val - self.min_val)))
        if new_val != self.value:
            self.value = new_val
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Renders the slider label, track, filled track, and thumb knob."""
        # 1. Render Header Label and Current Value
        lbl_surf = self.font.render(self.label, True, COLOR_TEXT_MUTED)
        val_surf = self.font_val.render(f"Nvl. {self.value}", True, COLOR_TEXT_PRIMARY)

        surface.blit(lbl_surf, (self.rect.x, self.rect.y - 22))
        surface.blit(val_surf, (self.rect.x + self.rect.width - val_surf.get_width(), self.rect.y - 22))

        # 2. Render Track
        track_y = self.rect.y + (self.rect.height // 2) - (self.track_height // 2)
        track_rect = pygame.Rect(self.rect.x, track_y, self.rect.width, self.track_height)
        pygame.draw.rect(surface, self.track_color, track_rect, border_radius=3)

        # 3. Render Filled Portion
        thumb_x = self._get_thumb_x()
        fill_width = thumb_x - self.rect.x
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, track_y, fill_width, self.track_height)
            pygame.draw.rect(surface, self.fill_color, fill_rect, border_radius=3)

        # 4. Render Thumb Knob
        thumb_center = (thumb_x, self.rect.y + self.rect.height // 2)
        pygame.draw.circle(surface, (20, 20, 20), thumb_center, self.thumb_radius + 1)  # Outer shadow
        pygame.draw.circle(surface, self.thumb_color, thumb_center, self.thumb_radius)


class Button:
    """Styled interactive push button."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Optional[Callable[[], None]] = None,
        bg_color: Tuple[int, int, int] = (45, 48, 58),
        hover_color: Tuple[int, int, int] = (62, 66, 80)
    ) -> None:
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.text: str = text
        self.callback: Optional[Callable[[], None]] = callback
        self.bg_color: Tuple[int, int, int] = bg_color
        self.hover_color: Tuple[int, int, int] = hover_color
        self.is_hovered: bool = False

        from config import get_font
        self.font: pygame.font.Font = get_font(14, bold=True)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Processes hover and click events for the button."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()

    def draw(self, surface: pygame.Surface) -> None:
        """Renders button surface with hover highlight and text label."""
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, (70, 75, 90), self.rect, width=1, border_radius=6)

        txt_surf = self.font.render(self.text, True, COLOR_TEXT_PRIMARY)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)
