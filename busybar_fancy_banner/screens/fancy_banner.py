"""Image-based banner supporting arbitrary fonts and PNG artwork."""

from __future__ import annotations
from busylib import converter

import hashlib
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps


DISPLAY_WIDTH = 72
DISPLAY_HEIGHT = 16



def _rgba(value: str) -> tuple[int, int, int, int]:
    """
    Accept #RRGGBB or #RRGGBBAA and return an RGBA tuple.
    """
    value = value.strip()

    if value.startswith("#") and len(value) == 9:
        return (
            int(value[1:3], 16),
            int(value[3:5], 16),
            int(value[5:7], 16),
            int(value[7:9], 16),
        )

    return ImageColor.getcolor(value, "RGBA")


@dataclass
class FancyBannerScreen:
    """
    Render a complete 72x16 image using Pillow.

    You may provide:
      - message only: arbitrary-font text banner
      - png_path only: PNG/image banner
      - both: PNG background/artwork with text overlaid
    """

    name: str = "fancy banner"

    message: str | None = None
    png_path: str | None = None

    font_path: str | None = None
    font_size: int = 10
    text_color: str = "#FFFFFFFF"

    background_color: str = "#000000FF"

    horizontal_align: str = "center"  # left, center, right
    vertical_align: str = "center"    # top, center, bottom

    x_offset: int = 0
    y_offset: int = 0

    image_fit: str = "contain"        # contain, cover, stretch, original
    image_anchor: str = "center"      # Pillow ImageOps.fit centering shortcut
    preserve_transparency: bool = True

    asset_filename: str = "fancy_banner.png"
    refresh_seconds: float | None = None

    _png_bytes: bytes = field(init=False, repr=False, default=b"")
    _last_hash: str | None = field(init=False, repr=False, default=None)
    _prepared: bool = field(init=False, repr=False, default=False)

    _uploaded_filename: str | None = field(
        init=False,
        repr=False,
        default=None,
    )

    def _load_font(self) -> ImageFont.ImageFont:
        if self.font_path:
            font_file = Path(self.font_path)

            if not font_file.exists():
                raise FileNotFoundError(
                    f"FancyBannerScreen font not found: {font_file}"
                )

            return ImageFont.truetype(
                str(font_file),
                self.font_size,
            )

        # Pillow's built-in fallback is deliberately available when no path
        # is supplied. For a genuinely different typeface, set font_path.
        return ImageFont.load_default()

    def _load_source_image(self) -> Image.Image | None:
        if not self.png_path:
            return None

        source_path = Path(self.png_path)

        if not source_path.exists():
            raise FileNotFoundError(
                f"FancyBannerScreen image not found: {source_path}"
            )

        return Image.open(source_path).convert("RGBA")

    def _place_source_image(
        self,
        canvas: Image.Image,
        source: Image.Image,
    ) -> None:
        fit = self.image_fit.lower()

        if fit == "stretch":
            placed = source.resize(
                (DISPLAY_WIDTH, DISPLAY_HEIGHT),
                Image.Resampling.LANCZOS,
            )
            position = (0, 0)

        elif fit == "cover":
            placed = ImageOps.fit(
                source,
                (DISPLAY_WIDTH, DISPLAY_HEIGHT),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
            position = (0, 0)

        elif fit == "original":
            placed = source
            position = (
                (DISPLAY_WIDTH - placed.width) // 2,
                (DISPLAY_HEIGHT - placed.height) // 2,
            )

        else:
            # contain
            placed = source.copy()
            placed.thumbnail(
                (DISPLAY_WIDTH, DISPLAY_HEIGHT),
                Image.Resampling.LANCZOS,
            )
            position = (
                (DISPLAY_WIDTH - placed.width) // 2,
                (DISPLAY_HEIGHT - placed.height) // 2,
            )

        if self.preserve_transparency:
            canvas.alpha_composite(placed, dest=position)
        else:
            canvas.paste(placed, position)

    def _text_position(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.ImageFont,
    ) -> tuple[int, int]:
        left, top, right, bottom = draw.textbbox(
            (0, 0),
            text,
            font=font,
        )

        text_width = right - left
        text_height = bottom - top

        horizontal = self.horizontal_align.lower()
        vertical = self.vertical_align.lower()

        if horizontal == "left":
            x = 0
        elif horizontal == "right":
            x = DISPLAY_WIDTH - text_width
        else:
            x = (DISPLAY_WIDTH - text_width) // 2

        if vertical == "top":
            y = -top
        elif vertical == "bottom":
            y = DISPLAY_HEIGHT - text_height - top
        else:
            y = (DISPLAY_HEIGHT - text_height) // 2 - top

        return x + self.x_offset, y + self.y_offset

    def _render_png(self) -> bytes:
        canvas = Image.new(
            "RGBA",
            (DISPLAY_WIDTH, DISPLAY_HEIGHT),
            _rgba(self.background_color),
        )

        source = self._load_source_image()
        if source is not None:
            self._place_source_image(canvas, source)

        if self.message:
            draw = ImageDraw.Draw(canvas)
            font = self._load_font()
            position = self._text_position(
                draw,
                self.message,
                font,
            )

            draw.text(
                position,
                self.message,
                font=font,
                fill=_rgba(self.text_color),
            )

        output = io.BytesIO()
        canvas.save(output, format="PNG")
        return output.getvalue()

    def prepare(
    self,
    upload: Callable[[str, bytes], None],
) -> None:
        png_bytes = self._render_png()
        digest = hashlib.sha256(png_bytes).hexdigest()

        if (
            digest == self._last_hash
            and self._prepared
            and self._uploaded_filename
        ):
            return

        # Convert the ordinary PNG into the storage format expected by
        # the BUSY Bar. The converter may also change the filename.
        converted_filename, converted_data = converter.convert_for_storage(
            self.asset_filename,
            png_bytes,
        )

        upload(
            converted_filename,
            converted_data,
        )

        self._png_bytes = png_bytes
        self._uploaded_filename = converted_filename
        self._last_hash = digest
        self._prepared = True

    def render(self) -> list[dict[str, Any]]:
        if not self._prepared or not self._uploaded_filename:
            raise RuntimeError(
                "FancyBannerScreen.render() was called before prepare()."
            )

        return [
            {
                "id": "main-screen",
                "type": "image",
                "path": self._uploaded_filename,
                "x": 0,
                "y": 0,
                "display": "front",
            }
        ]
