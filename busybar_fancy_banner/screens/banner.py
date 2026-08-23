"""Simple built-in-font banner screen."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BannerScreen:
    message: str
    name: str = "banner"
    font: str = "large"
    color: str = "#FFFFFFFF"
    x: int = 36
    y: int = 15
    align: str = "bottom_mid"
    width: int | None = None
    scroll_rate: int | None = None
    refresh_seconds: float | None = None

    def render(self) -> list[dict[str, Any]]:
        element: dict[str, Any] = {
            "id": "main-screen",
            "type": "text",
            "text": self.message,
            "x": self.x,
            "y": self.y,
            "font": self.font,
            "color": self.color,
            "align": self.align,
        }

        if self.width is not None:
            element["width"] = self.width

        if self.scroll_rate is not None:
            element["scroll_rate"] = self.scroll_rate

        return [element]
