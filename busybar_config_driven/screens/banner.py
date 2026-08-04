"""Configurable banner screen with optional horizontal scrolling."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


DISPLAY_WIDTH = 72


# Approximate average character widths for BUSY Bar fonts.
# These can be overridden in config.py using pixels_per_character.
DEFAULT_CHARACTER_WIDTHS = {
    "small": 4,
    "normal": 5,
    "large": 7,
    "extra_large": 9,
}


@dataclass
class BannerScreen:
    message: str

    name: str = "banner"

    font: str = "large"
    color: str = "#FFFFFFFF"

    y: int = 15
    align: str = "bottom_mid"

    # Where short, non-scrolling text is positioned.
    x: int = 36

    # Automatically scroll text that is wider than the display.
    auto_scroll: bool = True

    # Number of pixels the banner moves per redraw.
    scroll_step: int = 1

    # Time between scrolling frames.
    refresh_seconds: float | None = 0.08

    # Blank space after the text before it repeats.
    scroll_gap_pixels: int = 16

    # Override the estimated character width when necessary.
    # Leave as None to use DEFAULT_CHARACTER_WIDTHS.
    pixels_per_character: int | None = None

    # Internal scrolling position. This is not normally set in config.py.
    _scroll_x: int = field(
        init=False,
        repr=False,
        default=DISPLAY_WIDTH,
    )

    def estimated_text_width(self) -> int:
        character_width = self.pixels_per_character

        if character_width is None:
            character_width = DEFAULT_CHARACTER_WIDTHS.get(
                self.font,
                6,
            )

        return len(self.message) * character_width

    def should_scroll(self) -> bool:
        return (
            self.auto_scroll
            and self.estimated_text_width() > DISPLAY_WIDTH
        )

    def render(self) -> list[dict[str, Any]]:
        if not self.should_scroll():
            return [
                {
                    "id": "main-screen",
                    "type": "text",
                    "text": self.message,
                    "x": self.x,
                    "y": self.y,
                    "font": self.font,
                    "color": self.color,
                    "align": self.align,
                }
            ]

        text_width = self.estimated_text_width()

        element = {
            "id": "main-screen",
            "type": "text",
            "text": self.message,
            "x": self._scroll_x,
            "y": self.y,
            "font": self.font,
            "color": self.color,

            # The x-coordinate represents the left edge while scrolling.
            "align": "bottom_left",
        }

        self._scroll_x -= self.scroll_step

        # Once the entire message has moved beyond the left side,
        # place it back to the right and repeat.
        if self._scroll_x < -(text_width + self.scroll_gap_pixels):
            self._scroll_x = DISPLAY_WIDTH

        return [element]