"""Configurable clock screen."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class ClockScreen:
    name: str = "clock"

    time_format: str = "%H:%M:%S"

    font: str = "extra_large"
    color: str = "#FFFFFFFF"

    x: int = 36
    y: int = 15
    align: str = "bottom_mid"

    refresh_seconds: float | None = 1.0

    def render(self) -> list[dict[str, Any]]:
        current_time = time.strftime(
            self.time_format,
            time.localtime(),
        )

        return [
            {
                # All full-screen modules use the same ID.
                # This causes the BUSY Bar to replace the previous element.
                "id": "main-screen",
                "type": "text",
                "text": current_time,
                "x": self.x,
                "y": self.y,
                "font": self.font,
                "color": self.color,
                "align": self.align,
            }
        ]