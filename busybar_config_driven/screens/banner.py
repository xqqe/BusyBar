"""Configurable static text banner screen."""

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
    refresh_seconds: float | None = None

    def render(self) -> list[dict[str, Any]]:
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
