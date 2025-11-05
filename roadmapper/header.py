from dataclasses import dataclass, field
from typing import Optional

from roadmapper.painter import Painter


@dataclass
class Header:
    """Header section that can display a logo alongside title and subtitle text."""

    title: str
    subtitle: Optional[str] = None
    logo_path: Optional[str] = None
    logo_width: int = 80
    logo_height: int = 80
    padding_x: int = 24
    padding_y: int = 18
    logo_spacing: int = 16
    background_colour: Optional[str] = "#FFFFFF"
    divider_colour: Optional[str] = "#CCCCCC"

    _measured_height: float = field(default=0, init=False)
    _subtitle_font_size: int = field(default=0, init=False)

    def _measure(self, painter: Painter) -> float:
        """Measure the vertical height required for the header."""
        painter.set_font(
            painter.title_font, painter.title_font_size, painter.title_font_colour
        )
        _, title_height = painter.get_text_dimension(self.title or "")

        subtitle_height = 0
        if self.subtitle:
            subtitle_font_size = max(painter.title_font_size - 4, 10)
            painter.set_font(
                painter.title_font, subtitle_font_size, painter.timeline_font_colour
            )
            _, subtitle_height = painter.get_text_dimension(self.subtitle)
            self._subtitle_font_size = subtitle_font_size
        else:
            self._subtitle_font_size = 0

        text_block_height = title_height + (subtitle_height + 6 if self.subtitle else 0)
        content_height = max(self.logo_height, text_block_height)
        self._measured_height = content_height + (self.padding_y * 2)
        return self._measured_height

    def draw(self, painter: Painter) -> None:
        """Draw the header onto the canvas."""
        header_height = self._measure(painter)
        content_height = header_height - (self.padding_y * 2)

        if self.background_colour:
            painter.set_colour(self.background_colour)
            painter.draw_box(0, 0, painter.width, header_height)

        content_x = float(self.padding_x)
        if self.logo_path:
            logo_y = self.padding_y + max(
                (content_height - self.logo_height) / 2.0, 0.0
            )
            painter.draw_image(
                self.logo_path, content_x, logo_y, self.logo_width, self.logo_height
            )
            content_x += self.logo_width + self.logo_spacing

        title_baseline = self.padding_y + painter.title_font_size
        painter.set_font(
            painter.title_font, painter.title_font_size, painter.title_font_colour
        )
        painter.draw_text(int(content_x), int(title_baseline), self.title)

        if self.subtitle:
            subtitle_baseline = (
                title_baseline + self._subtitle_font_size + 4
            )
            painter.set_font(
                painter.title_font,
                self._subtitle_font_size,
                painter.timeline_font_colour,
            )
            painter.draw_text(int(content_x), int(subtitle_baseline), self.subtitle)

        if self.divider_colour:
            painter.set_colour(self.divider_colour)
            painter.set_line_width(1)
            painter.draw_line(0, header_height, painter.width, header_height)

        painter.last_drawn_y_pos = header_height

    def measure(self, painter: Painter) -> float:
        """Public helper to measure height without drawing."""
        return self._measure(painter)

    @property
    def height(self) -> float:
        return self._measured_height
