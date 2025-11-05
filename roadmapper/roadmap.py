# MIT License

# Copyright (c) 2022 CS Goh

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from contextlib import contextmanager
from typing import Optional

from roadmapper.painter import Painter
from roadmapper.title import Title, Subtitle
from roadmapper.footer import Footer
from roadmapper.timelinemode import TimelineMode
from roadmapper.timeline import Timeline
from roadmapper.group import Group
from roadmapper.marker import Marker
from roadmapper.header import Header


@dataclass()
class Roadmap:
    """The main Roadmap class"""

    width: int = field(default=1200)
    height: int = field(default=600)
    colour_theme: str = field(default="DEFAULT")
    show_marker: bool = field(default=True)

    title: Title = field(default=None, init=False)
    subtitle: Subtitle = field(default=None, init=False)
    timeline: Timeline = field(default=None, init=False)
    groups: list[Group] = field(default_factory=list, init=False)
    footer: Footer = field(default=None, init=False)
    marker: Marker = field(default=None, init=False)
    header: Header = field(default=None, init=False)

    __version__ = "v0.1.1"

    def __post_init__(self):
        """This method is called after __init__() is called"""
        self.__painter = Painter(self.width, self.height)
        self.__set_colour_palette(self.colour_theme)
        self.groups = []
        self._pdf_body_font = "Helvetica"
        self._pdf_body_font_file = ""
        self._font_family = self.__painter.title_font
        self._component_fonts = {}
        self._font_files: dict[str, str] = {}
        self._tag_palette: dict[str, str] = {}
        self._tag_default_sequence: list[str] = [
            "#1F77B4",
            "#2CA02C",
            "#D62728",
            "#9467BD",
            "#FF7F0E",
            "#17BECF",
            "#BCBD22",
            "#8C564B",
        ]
        self._tag_auto_palette: dict[str, str] = {}
        if self.show_marker == True:
            self.__create_marker()

    def __set_colour_palette(self, palette: str) -> None:
        """This method sets the colour palette"""
        self.__painter.set_colour_palette(palette)
        # Override with CLA custom palette
        accent_timeline = "#2E334E"
        accent_task = "#24787A"
        accent_milestone = "#39A5A7"

        self.__painter.timeline_fill_colour = accent_timeline
        self.__painter.timeline_font_colour = "#FFFFFF"

        self.__painter.group_fill_colour = accent_timeline
        self.__painter.group_font_colour = "#FFFFFF"

        self.__painter.task_fill_colour = accent_task
        self.__painter.task_font_colour = "#FFFFFF"

        self.__painter.milestone_fill_colour = accent_milestone
        self.__painter.milestone_font_colour = "#FFFFFF"

        if self.marker is not None:
            self.marker.line_colour = accent_milestone
            self.marker.font_colour = accent_milestone

    def __create_marker(
        self,
        label_text_font: str = "",
        label_text_colour: str = "",
        label_text_size: int = 0,
        line_colour: str = "",
        line_width: int = 2,
        line_style: str = "dashed",
    ) -> None:
        """Add and configure the marker settings

        Args:
            label_text_font (str, optional): Label text font. Defaults to "Arial".
            label_text_colour (str, optional): Label text colour. Defaults to "Black".
            label_text_size (int, optional): Label text size. Defaults to 10.
            line_colour (str, optional): Line colour. Defaults to "Black".
            line_width (int, optional): Line width. Defaults to 2.
            line_style (str, optional): Line style. Defaults to "solid". Options are "solid", "dashed"
        """
        if label_text_font == "":
            label_text_font = self.__painter.marker_font
        if label_text_size == 0:
            label_text_size = self.__painter.marker_font_size
        if label_text_colour == "":
            label_text_colour = self.__painter.marker_font_colour
        if line_colour == "":
            line_colour = self.__painter.marker_line_colour

        self.marker = Marker(
            font=label_text_font,
            font_size=label_text_size,
            font_colour=label_text_colour,
            line_colour=line_colour,
            line_width=line_width,
            line_style=line_style,
        )

    def set_marker(
        self,
        label_text_font: str = "",
        label_text_colour: str = "",
        label_text_size: int = 0,
        line_colour: str = "",
        line_width: int = 2,
        line_style: str = "dashed",
    ) -> None:
        """Configure the marker settings

        Args:
            label_text_font (str, optional): Label text font. Defaults to "Arial".
            label_text_colour (str, optional): Label text colour. Defaults to "Black".
            label_text_size (int, optional): Label text size. Defaults to 10.
            line_colour (str, optional): Line colour. Defaults to "Black".
            line_width (int, optional): Line width. Defaults to 2.
            line_style (str, optional): Line style. Defaults to "solid". Options are "solid", "dashed"
        """
        if label_text_font == "":
            label_text_font = self.__painter.marker_font
        if label_text_size == 0:
            label_text_size = self.__painter.marker_font_size
        if label_text_colour == "":
            label_text_colour = self.__painter.marker_font_colour
        if line_colour == "":
            line_colour = self.__painter.marker_line_colour

        self.marker.font = label_text_font
        self.marker.font_size = label_text_size
        self.font_colour = label_text_colour
        self.line_colour = line_colour
        self.line_width = line_width
        self.line_style = line_style

    def set_fonts(
        self,
        family: str = "",
        component_fonts: dict[str, str] = None,
        pdf_font_name: str = "",
        pdf_font_file: str = "",
        font_files: dict[str, str] = None,
    ) -> None:
        """Override the font families used by roadmap components."""
        font_files = font_files or {}
        if family:
            self._font_family = family
        if component_fonts:
            self._component_fonts = component_fonts
        if font_files:
            self._font_files.update(font_files)
        self.__painter.override_fonts(family, component_fonts or {}, font_files)
        if pdf_font_name:
            self._pdf_body_font = pdf_font_name
        elif family:
            self._pdf_body_font = family
        if pdf_font_file:
            self._pdf_body_font_file = pdf_font_file

    def set_tag_styles(
        self,
        palette: Optional[dict[str, str]] = None,
        default_colours: Optional[list[str]] = None,
    ) -> None:
        """Configure colour palette used when rendering tag chips."""
        palette = palette or {}
        self._tag_palette = {
            str(tag): str(colour)
            for tag, colour in palette.items()
            if tag and colour
        }
        if default_colours:
            filtered = [colour for colour in default_colours if colour]
            if filtered:
                self._tag_default_sequence = filtered
        if not getattr(self, "_tag_default_sequence", None):
            self._tag_default_sequence = ["#1F77B4"]
        self._tag_auto_palette = {}

    def _resolve_tag_colour(self, tag: str) -> str:
        """Return a hex colour associated with the provided tag."""
        if not tag:
            return "#2E334E"
        key = str(tag)
        if key in self._tag_palette:
            return self._tag_palette[key]
        if key in self._tag_auto_palette:
            return self._tag_auto_palette[key]
        palette = self._tag_default_sequence or ["#1F77B4"]
        index = len(self._tag_auto_palette) % len(palette)
        colour = palette[index]
        self._tag_auto_palette[key] = colour
        return colour

    def set_header(
        self,
        logo_path: str = "",
        logo_width: int = 80,
        logo_height: int = 80,
        background_colour: str = "#FFFFFF",
        divider_colour: str = "#CCCCCC",
        padding_x: int = 24,
        padding_y: int = 18,
        logo_spacing: int = 16,
        title: str = "",
        subtitle: str = "",
    ) -> None:
        """Configure an optional header area that includes a logo and title text."""
        header_title = title or (self.title.text if self.title else "")
        if header_title == "":
            raise ValueError("Header title cannot be empty.")

        header_subtitle = subtitle or ""
        if header_subtitle == "" and self.subtitle is not None:
            header_subtitle = self.subtitle.text
        if header_subtitle == "":
            header_subtitle = None

        self.title = Title(
            text=header_title,
            font=self.__painter.title_font,
            font_size=self.__painter.title_font_size,
            font_colour=self.__painter.title_font_colour,
        )

        if header_subtitle:
            subtitle_font_size = max(self.__painter.title_font_size - 4, 10)
            self.subtitle = Subtitle(
                text=header_subtitle,
                font=self.__painter.title_font,
                font_size=subtitle_font_size,
                font_colour=self.__painter.timeline_font_colour,
            )
        else:
            self.subtitle = None

        self.header = Header(
            title=header_title,
            subtitle=header_subtitle,
            logo_path=logo_path or None,
            logo_width=int(logo_width),
            logo_height=int(logo_height),
            padding_x=int(padding_x),
            padding_y=int(padding_y),
            logo_spacing=int(logo_spacing),
            background_colour=background_colour,
            divider_colour=divider_colour,
        )
        measured_height = self.header.measure(self.__painter)
        self.__painter.last_drawn_y_pos = measured_height

    def set_title(
        self,
        text: str,
        font: str = "",
        font_size: int = 0,
        font_colour: str = "",
    ) -> None:
        """Configure the title settings

        Args:
            text (str): Title text
            font (str, optional): Title font. Defaults to "Arial".
            font_size (int, optional): Title font size. Defaults to 18.
            font_colour (str, optional): Title font colour. Defaults to "Black".
        """
        if font == "":
            font = self.__painter.title_font
        if font_size == 0:
            font_size = self.__painter.title_font_size
        if font_colour == "":
            font_colour = self.__painter.title_font_colour

        self.title = Title(
            text=text, font=font, font_size=font_size, font_colour=font_colour
        )
        self.title.text = text

        if self.header is None:
            self.title.set_draw_position(self.__painter)

    def set_subtitle(
        self,
        text: str,
        font: str = "",
        font_size: int = 0,
        font_colour: str = "",
    ) -> None:
        """Configure the subtitle settings."""
        if font == "":
            font = self.__painter.title_font
        if font_size == 0:
            font_size = max(self.__painter.title_font_size - 6, 10)
        if font_colour == "":
            font_colour = self.__painter.title_font_colour

        self.subtitle = Subtitle(
            text=text,
            font=font,
            font_size=font_size,
            font_colour=font_colour,
        )
        if self.header is None:
            self.subtitle.set_draw_position(self.__painter)

    def set_footer(
        self,
        text: str,
        font: str = "",
        font_size: int = 0,
        font_colour: str = "",
    ) -> None:
        """Configure the footer settings

        Args:
            text (str): Footer text
            font (str, optional): Footer font. Defaults to "Arial".
            font_size (int, optional): Footer font size. Defaults to 18.
            font_colour (str, optional): Footer font colour. Defaults to "Black".
        """
        if font == "":
            font = self.__painter.footer_font
        if font_size == 0:
            font_size = self.__painter.footer_font_size
        if font_colour == "":
            font_colour = self.__painter.footer_font_colour

        self.footer = Footer(
            text=text, font=font, font_size=font_size, font_colour=font_colour
        )
        self.footer.text = text

    def set_timeline(
        self,
        mode: TimelineMode = TimelineMode.MONTHLY,
        start: datetime = datetime.strptime(
            datetime.strftime(datetime.today(), "%Y-%m-%d"), "%Y-%m-%d"
        ),
        number_of_items: int = 12,
        show_generic_dates: bool = False,
        font: str = "",
        font_size: int = 0,
        font_colour: str = "",
        fill_colour: str = "",
    ) -> None:
        """Configure the timeline settings

        Args:
            mode (TimelineMode, optional): Timeline mode. Defaults to TimelineMode.MONTHLY.
                                            Options are WEEKLY, MONTHLY, QUARTERLY, HALF_YEARLY, YEARLY
            start (datetime, optional): Timeline start date. Defaults to current date
            number_of_items (int, optional): Number of time periods to display on the timeline. Defaults to 12.
            font (str, optional): Timeline font. Defaults to "Arial".
            font_size (int, optional): Timeline font size. Defaults to 10.
            font_colour (str, optional): Timeline font colour. Defaults to "Black".
            fill_colour (str, optional): Timeline fill colour. Defaults to "lightgrey".
        """
        if font == "":
            font = self.__painter.timeline_font
        if font_size == 0:
            font_size = self.__painter.timeline_font_size
        if font_colour == "":
            font_colour = self.__painter.timeline_font_colour
        if fill_colour == "":
            fill_colour = self.__painter.timeline_fill_colour

        start_date = datetime.strptime(start, "%Y-%m-%d")
        self.timeline = Timeline(
            mode=mode,
            start=start_date,
            number_of_items=number_of_items,
            show_generic_dates=show_generic_dates,
            font=font,
            font_size=font_size,
            font_colour=font_colour,
            fill_colour=fill_colour,
        )
        if self.header is not None:
            self.__painter.last_drawn_y_pos = self.header.height
        self.timeline.set_draw_position(self.__painter)
        if self.marker != None:
            self.marker.set_label_draw_position(self.__painter, self.timeline)

    def add_group(
        self,
        text: str,
        font: str = "",
        font_size: int = 0,
        font_colour: str = "",
        fill_colour: str = "",
        text_alignment: str = "centre",
    ) -> Group:
        """Add new group to the roadmap

        Args:
            text (str): Group text
            font (str, optional): Group text font. Defaults to "Arial".
            font_size (int, optional): Group text font size. Defaults to 10.
            font_colour (str, optional): Group text font colour. Defaults to "Black".
            fill_colour (str, optional): Group fill colour. Defaults to "lightgrey".
            text_alignment (str, optional): Group text alignment. Defaults to "centre". Options are "left", "centre", "right"

        Return:
            Group: A new group instance. Use this to add taks to the group
        """
        if font == "":
            font = self.__painter.group_font
        if font_size == 0:
            font_size = self.__painter.group_font_size
        if font_colour == "":
            font_colour = self.__painter.group_font_colour
        if fill_colour == "":
            fill_colour = self.__painter.group_fill_colour

        group = Group(
            text=text,
            font=font,
            font_size=font_size,
            font_colour=font_colour,
            fill_colour=fill_colour,
            text_alignment=text_alignment,
            painter=self.__painter,
        )
        self.groups.append(group)
        # group.set_draw_position(self.__painter, self.timeline)

        return group

    def draw(self) -> None:
        """Draw the roadmap"""
        self.__painter.set_background_colour()

        if self.header is not None:
            self.header.draw(self.__painter)
        else:
            if self.title == None:
                raise ValueError("Title is not set. Please call set_title() to set title.")
            self.title.draw(self.__painter)
            if self.subtitle is not None:
                self.subtitle.draw(self.__painter)

        if self.timeline == None:
            raise ValueError(
                "Timeline is not set. Please call set_timeline() to set timeline."
            )
        self.timeline.set_draw_position(self.__painter)
        self.timeline.draw(self.__painter)

        for group in self.groups:
            group.set_draw_position(self.__painter, self.timeline)
            group.draw(self.__painter)

        if self.marker != None:
            self.marker.set_line_draw_position(self.__painter)
            self.marker.draw(self.__painter)

        if self.footer != None:
            self.footer.set_draw_position(self.__painter)
            self.footer.draw(self.__painter)

    def iter_tasks(self):
        """Yield all tasks contained in the roadmap."""
        for group in self.groups:
            yield from group.iter_tasks()

    def __detail_tasks(self):
        """Return tasks that have detail content configured."""
        return [
            task
            for task in self.iter_tasks()
            if hasattr(task, "has_detail") and task.has_detail
        ]

    def __collect_font_names(self) -> dict[str, str]:
        base = self._font_family or self.__painter.title_font
        fonts = {
            "title": self._component_fonts.get("title", base),
            "timeline": self._component_fonts.get("timeline", base),
            "group": self._component_fonts.get("group", base),
            "task": self._component_fonts.get("task", base),
            "milestone": self._component_fonts.get("milestone", base),
        }
        fonts.setdefault("body", fonts.get("task", base))
        if self.marker is not None:
            fonts["marker"] = self.marker.font
        else:
            fonts["marker"] = fonts["timeline"]
        return fonts

    def __draw_pdf_header_block(
        self,
        pdf_canvas,
        header_obj,
        heading_font_name: str,
        subtitle_font_name: str,
    ) -> float:
        from reportlab.lib import colors

        if header_obj is None:
            return float(self.height)

        header_height = header_obj.height or header_obj.measure(self.__painter)
        header_top = float(self.height)
        header_bottom = header_top - header_height

        bg_colour = header_obj.background_colour or self.__painter.background_colour
        pdf_canvas.saveState()
        pdf_canvas.setFillColor(colors.HexColor(bg_colour))
        pdf_canvas.rect(0, header_bottom, self.width, header_height, stroke=0, fill=1)
        pdf_canvas.restoreState()

        content_x = float(header_obj.padding_x)
        content_height = header_height - (header_obj.padding_y * 2)
        if header_obj.logo_path:
            logo_y = header_bottom + header_obj.padding_y + max(
                (content_height - header_obj.logo_height) / 2.0, 0.0
            )
            pdf_canvas.drawImage(
                header_obj.logo_path,
                content_x,
                logo_y,
                width=header_obj.logo_width,
                height=header_obj.logo_height,
                preserveAspectRatio=True,
                mask="auto",
            )
            content_x += header_obj.logo_width + header_obj.logo_spacing

        title_baseline = header_bottom + header_obj.padding_y + self.__painter.title_font_size
        pdf_canvas.setFont(heading_font_name, self.__painter.title_font_size)
        pdf_canvas.setFillColor(colors.HexColor(self.__painter.title_font_colour))
        pdf_canvas.drawString(content_x, title_baseline, header_obj.title)

        if header_obj.subtitle:
            subtitle_font_size = max(self.__painter.title_font_size - 4, 10)
            subtitle_baseline = title_baseline - subtitle_font_size - 4
            pdf_canvas.setFont(subtitle_font_name, subtitle_font_size)
            pdf_canvas.setFillColor(colors.HexColor(self.__painter.timeline_font_colour))
            pdf_canvas.drawString(content_x, subtitle_baseline, header_obj.subtitle)

        if header_obj.divider_colour:
            pdf_canvas.setStrokeColor(colors.HexColor(header_obj.divider_colour))
            pdf_canvas.setLineWidth(1)
            pdf_canvas.line(0, header_bottom, self.width, header_bottom)

        return header_bottom

    def __draw_on_canvas(
        self,
        pdf_canvas,
        fonts_map: dict[str, str],
        body_font_name: str,
        heading_font_name: str,
    ) -> None:
        from reportlab.lib import colors

        height = self.height
        width = self.width

        def to_pdf_y(y: float) -> float:
            return height - y

        def rect_y(y: float, h: float) -> float:
            return height - (y + h)

        pdf_canvas.saveState()
        pdf_canvas.setFillColor(colors.HexColor(self.__painter.background_colour))
        pdf_canvas.rect(0, 0, width, height, stroke=0, fill=1)
        pdf_canvas.restoreState()

        title_font = fonts_map.get("title", heading_font_name)
        timeline_font = fonts_map.get("timeline", body_font_name)
        group_font = fonts_map.get("group", body_font_name)
        task_font = fonts_map.get("task", body_font_name)
        milestone_font = fonts_map.get("milestone", body_font_name)
        marker_font = fonts_map.get("marker", timeline_font)

        # Header or title/subtitle
        if self.header is not None:
            header_height = self.header.height or 0
            header_top = height
            header_bottom = header_top - header_height
            bg_colour = self.header.background_colour or self.__painter.background_colour
            pdf_canvas.saveState()
            pdf_canvas.setFillColor(colors.HexColor(bg_colour))
            pdf_canvas.rect(0, header_bottom, width, header_height, stroke=0, fill=1)
            pdf_canvas.restoreState()

            content_x = float(self.header.padding_x)
            if self.header.logo_path:
                logo_y = header_top - self.header.padding_y - self.header.logo_height
                pdf_canvas.drawImage(
                    self.header.logo_path,
                    content_x,
                    logo_y,
                    width=self.header.logo_width,
                    height=self.header.logo_height,
                    preserveAspectRatio=True,
                    mask="auto",
                )
                content_x += self.header.logo_width + self.header.logo_spacing

            title_baseline = to_pdf_y(self.header.padding_y + self.__painter.title_font_size)
            pdf_canvas.setFont(title_font, self.__painter.title_font_size)
            pdf_canvas.setFillColor(colors.HexColor(self.__painter.title_font_colour))
            pdf_canvas.drawString(content_x, title_baseline, self.header.title)

            if self.header.subtitle:
                subtitle_font_size = max(self.__painter.title_font_size - 4, 10)
                subtitle_baseline = to_pdf_y(
                    self.header.padding_y + self.__painter.title_font_size + subtitle_font_size + 4
                )
                pdf_canvas.setFont(timeline_font, subtitle_font_size)
                pdf_canvas.setFillColor(colors.HexColor(self.__painter.timeline_font_colour))
                pdf_canvas.drawString(content_x, subtitle_baseline, self.header.subtitle)

            if self.header.divider_colour:
                pdf_canvas.setStrokeColor(colors.HexColor(self.header.divider_colour))
                pdf_canvas.setLineWidth(1)
                pdf_canvas.line(0, header_bottom, width, header_bottom)
        else:
            if self.title is not None:
                pdf_canvas.setFont(title_font, self.title.font_size)
                pdf_canvas.setFillColor(colors.HexColor(self.title.font_colour))
                pdf_canvas.drawString(self.title.x, to_pdf_y(self.title.y), self.title.text)
            if self.subtitle is not None:
                pdf_canvas.setFont(timeline_font, self.subtitle.font_size)
                pdf_canvas.setFillColor(colors.HexColor(self.subtitle.font_colour))
                pdf_canvas.drawString(
                    self.subtitle.x,
                    to_pdf_y(self.subtitle.y),
                    self.subtitle.text,
                )

        # Timeline
        if self.timeline is not None:
            pdf_canvas.setFont(timeline_font, self.timeline.font_size)
            pdf_canvas.setFillColor(colors.HexColor(self.__painter.timeline_font_colour))
            for timeline_item in self.timeline.timeline_items:
                pdf_canvas.saveState()
                pdf_canvas.setFillColor(colors.HexColor(self.__painter.timeline_fill_colour))
                pdf_canvas.rect(
                    timeline_item.box_x,
                    rect_y(timeline_item.box_y, timeline_item.box_height),
                    timeline_item.box_width,
                    timeline_item.box_height,
                    stroke=0,
                    fill=1,
                )
                pdf_canvas.restoreState()
                pdf_canvas.setFillColor(colors.HexColor(self.__painter.timeline_font_colour))
                pdf_canvas.drawString(
                    timeline_item.text_x,
                    to_pdf_y(timeline_item.text_y),
                    timeline_item.text,
                )

        # Groups and tasks
        for group in self.groups:
            pdf_canvas.saveState()
            pdf_canvas.setFillColor(colors.HexColor(group.fill_colour))
            pdf_canvas.rect(
                group.box_x,
                rect_y(group.box_y, group.box_height),
                group.box_width,
                group.box_height,
                stroke=0,
                fill=1,
            )
            pdf_canvas.restoreState()
            pdf_canvas.setFont(group_font, group.font_size)
            pdf_canvas.setFillColor(colors.HexColor(group.font_colour))
            pdf_canvas.drawString(group.text_x, to_pdf_y(group.text_y), group.text)

            for task in group.tasks:
                pdf_canvas.saveState()
                pdf_canvas.setFillColor(colors.HexColor(task.fill_colour))
                for box_x, box_y, box_width, box_height in task.boxes:
                    pdf_canvas.rect(
                        box_x,
                        rect_y(box_y, box_height),
                        box_width,
                        box_height,
                        stroke=0,
                        fill=1,
                    )
                pdf_canvas.restoreState()
                pdf_canvas.setFont(task_font, task.font_size)
                pdf_canvas.setFillColor(colors.HexColor(task.font_colour))
                pdf_canvas.drawString(task.text_x, to_pdf_y(task.text_y), task.text)

                for milestone in task.milestones:
                    pdf_canvas.saveState()
                    pdf_canvas.setFillColor(colors.HexColor(milestone.fill_colour))
                    path = pdf_canvas.beginPath()
                    x = milestone.diamond_x
                    y = rect_y(milestone.diamond_y, milestone.diamond_height)
                    w = milestone.diamond_width
                    h = milestone.diamond_height
                    path.moveTo(x + w / 2, y + h)
                    path.lineTo(x + w, y + h / 2)
                    path.lineTo(x + w / 2, y)
                    path.lineTo(x, y + h / 2)
                    path.close()
                    pdf_canvas.drawPath(path, stroke=0, fill=1)
                    pdf_canvas.restoreState()
                    pdf_canvas.setFont(milestone_font, milestone.font_size)
                    pdf_canvas.setFillColor(colors.HexColor(milestone.font_colour))
                    pdf_canvas.drawString(
                        milestone.text_x,
                        to_pdf_y(milestone.text_y),
                        milestone.text,
                    )

                for parallel_task in task.tasks:
                    pdf_canvas.saveState()
                    pdf_canvas.setFillColor(colors.HexColor(parallel_task.fill_colour))
                    for box_x, box_y, box_width, box_height in parallel_task.boxes:
                        pdf_canvas.rect(
                            box_x,
                            rect_y(box_y, box_height),
                            box_width,
                            box_height,
                            stroke=0,
                            fill=1,
                        )
                    pdf_canvas.restoreState()
                    pdf_canvas.setFont(task_font, parallel_task.font_size)
                    pdf_canvas.setFillColor(colors.HexColor(parallel_task.font_colour))
                    pdf_canvas.drawString(
                        parallel_task.text_x,
                        to_pdf_y(parallel_task.text_y),
                        parallel_task.text,
                    )
                    for pt_milestone in parallel_task.milestones:
                        pdf_canvas.saveState()
                        pdf_canvas.setFillColor(colors.HexColor(pt_milestone.fill_colour))
                        path = pdf_canvas.beginPath()
                        x = pt_milestone.diamond_x
                        y = rect_y(pt_milestone.diamond_y, pt_milestone.diamond_height)
                        w = pt_milestone.diamond_width
                        h = pt_milestone.diamond_height
                        path.moveTo(x + w / 2, y + h)
                        path.lineTo(x + w, y + h / 2)
                        path.lineTo(x + w / 2, y)
                        path.lineTo(x, y + h / 2)
                        path.close()
                        pdf_canvas.drawPath(path, stroke=0, fill=1)
                        pdf_canvas.restoreState()
                        pdf_canvas.setFont(milestone_font, pt_milestone.font_size)
                        pdf_canvas.setFillColor(colors.HexColor(pt_milestone.font_colour))
                        pdf_canvas.drawString(
                            pt_milestone.text_x,
                            to_pdf_y(pt_milestone.text_y),
                            pt_milestone.text,
                        )

        # Marker
        if self.marker is not None:
            pdf_canvas.saveState()
            pdf_canvas.setFont(marker_font, self.marker.font_size)
            pdf_canvas.setFillColor(colors.HexColor(self.marker.font_colour))
            pdf_canvas.drawString(
                self.marker.label_x,
                to_pdf_y(self.marker.label_y + 10),
                self.marker.text,
            )
            pdf_canvas.setStrokeColor(colors.HexColor(self.marker.line_colour))
            pdf_canvas.setLineWidth(self.marker.line_width)
            pdf_canvas.line(
                self.marker.line_from_x,
                to_pdf_y(self.marker.line_from_y),
                self.marker.line_to_x,
                to_pdf_y(self.marker.line_to_y),
            )
            pdf_canvas.restoreState()

        if self.footer is not None:
            pdf_canvas.setFont(fonts_map.get("group", body_font_name), self.footer.font_size)
            pdf_canvas.setFillColor(colors.HexColor(self.footer.font_colour))
            pdf_canvas.drawString(
                self.footer.x,
                to_pdf_y(self.footer.y),
                self.footer.text,
            )

    def __save_pdf(self, output_path: Path) -> None:
        """Generate an interactive PDF with clickable roadmap items."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
            from reportlab.lib.utils import simpleSplit
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
        except ImportError as exc:  # pragma: no cover - guarded for runtime feedback
            raise RuntimeError(
                "reportlab is required to export interactive PDFs."
            ) from exc

        pdf_canvas = canvas.Canvas(str(output_path), pagesize=(self.width, self.height))
        document_title = self.title.text if self.title else output_path.stem
        pdf_canvas.setTitle(document_title)
        pdf_canvas.setPageSize((self.width, self.height))
        pdf_canvas.bookmarkPage("roadmap_overview")
        pdf_canvas.addOutlineEntry(
            document_title, "roadmap_overview", level=0, closed=False
        )

        detail_tasks = self.__detail_tasks()
        fonts_map = self.__collect_font_names()
        component_font_files = self._font_files
        nested_artifacts = {}
        for task in detail_tasks:
            builder = getattr(task, "detail_roadmap_builder", None)
            if builder is None:
                continue
            try:
                nested_roadmap = builder()
            except Exception as exc:  # pragma: no cover - runtime guard
                raise RuntimeError(
                    f"Failed to build detail roadmap for task '{task.text}'."
                ) from exc
            if nested_roadmap is None:
                continue
            if not isinstance(nested_roadmap, Roadmap):
                raise TypeError(
                    "Detail roadmap builder must return a Roadmap instance."
                )
            nested_roadmap.draw()
            nested_artifacts[task.identifier] = nested_roadmap

        def ensure_pdf_font(font_name: str, font_file: str) -> str:
            candidate = font_name or "Helvetica"
            if candidate in pdfmetrics.getRegisteredFontNames():
                return candidate
            if candidate in pdfmetrics.standardFonts:
                return candidate
            if font_file:
                try:
                    pdfmetrics.registerFont(TTFont(candidate, font_file))
                    return candidate
                except Exception:
                    return "Helvetica"
            return "Helvetica"

        def ensure_fonts_for(font_name: str) -> str:
            if not font_name:
                return ensure_pdf_font("Helvetica", "")
            file_path = component_font_files.get(font_name, "")
            if not file_path and font_name == getattr(self, "_pdf_body_font", ""):
                file_path = getattr(self, "_pdf_body_font_file", "")
            return ensure_pdf_font(font_name, file_path)

        body_font_name = ensure_fonts_for(
            getattr(self, "_pdf_body_font", fonts_map.get("task", ""))
        )
        fonts_map["body"] = body_font_name
        heading_font_name = ensure_fonts_for(fonts_map.get("title", body_font_name))
        fonts_map["title"] = heading_font_name
        fonts_map["timeline"] = ensure_fonts_for(fonts_map.get("timeline", body_font_name))
        fonts_map["group"] = ensure_fonts_for(fonts_map.get("group", body_font_name))
        fonts_map["task"] = ensure_fonts_for(fonts_map.get("task", body_font_name))
        fonts_map["milestone"] = ensure_fonts_for(fonts_map.get("milestone", body_font_name))
        if self.marker is not None:
            fonts_map["marker"] = ensure_fonts_for(self.marker.font)
        else:
            fonts_map["marker"] = fonts_map["timeline"]

        def draw_nav_button(
            text: str,
            destination: str,
            x: float,
            y: float,
            width: float = 200,
            height: float = 28,
            font_name: str = heading_font_name,
            font_size: int = 12,
        ) -> None:
            pdf_canvas.setFillColor(colors.HexColor("#1f77b4"))
            pdf_canvas.roundRect(
                x,
                y,
                width,
                height,
                radius=6,
                fill=1,
                stroke=0,
            )
            pdf_canvas.setFillColor(colors.white)
            pdf_canvas.setFont(font_name, font_size)
            text_width = pdf_canvas.stringWidth(text, font_name, font_size)
            pdf_canvas.drawString(
                x + (width - text_width) / 2,
                y + (height - font_size) / 2 + 4,
                text,
            )
            pdf_canvas.linkRect(
                contents=text,
                destinationname=destination,
                Rect=(x, y, x + width, y + height),
                relative=0,
                thickness=0,
            )
            pdf_canvas.setFillColor(colors.black)

        def draw_tag_chips(
            tags: list[str],
            *,
            start_x: float,
            start_y: float,
            max_x: float,
            font_name: str,
            font_size: int = 10,
        ) -> float:
            """Render tag chips and return the next baseline y-position."""
            if not tags:
                return start_y

            unique_labels = []
            seen = set()
            for raw in tags:
                label = str(raw).strip()
                if not label or label in seen:
                    continue
                seen.add(label)
                unique_labels.append(label)

            if not unique_labels:
                return start_y

            padding_x = 6
            padding_y = 3
            gap_x = 6
            line_height = font_size + (padding_y * 2)

            pdf_canvas.setFont(font_name, font_size)

            current_x = start_x
            line_top = start_y
            lowest_y = line_top - line_height

            for label in unique_labels:
                colour_value = self._resolve_tag_colour(label)
                try:
                    fill_colour = colors.toColor(colour_value)
                except Exception:  # pragma: no cover - defensive conversion
                    fill_colour = colors.HexColor("#2E334E")

                chip_width = (
                    pdf_canvas.stringWidth(label, font_name, font_size)
                    + (padding_x * 2)
                )

                if current_x + chip_width > max_x and current_x > start_x:
                    current_x = start_x
                    line_top -= line_height + 4

                chip_bottom = line_top - line_height
                pdf_canvas.setFillColor(fill_colour)
                pdf_canvas.roundRect(
                    current_x,
                    chip_bottom,
                    chip_width,
                    line_height,
                    radius=line_height / 2,
                    stroke=0,
                    fill=1,
                )

                luminance = (
                    (0.299 * fill_colour.red)
                    + (0.587 * fill_colour.green)
                    + (0.114 * fill_colour.blue)
                )
                text_colour = colors.white if luminance < 0.6 else colors.black
                pdf_canvas.setFillColor(text_colour)
                pdf_canvas.drawString(
                    current_x + padding_x,
                    chip_bottom + padding_y + (font_size * 0.1),
                    label,
                )

                lowest_y = min(lowest_y, chip_bottom)
                current_x += chip_width + gap_x

            pdf_canvas.setFillColor(colors.black)
            return lowest_y - 10

        self.__draw_on_canvas(pdf_canvas, fonts_map, body_font_name, heading_font_name)

        for task in detail_tasks:
            for box_x, box_y, box_width, box_height in task.boxes:
                if box_width <= 0 or box_height <= 0:
                    continue
                rect = (
                    box_x,
                    self.height - (box_y + box_height),
                    box_x + box_width,
                    self.height - box_y,
                )
                pdf_canvas.linkRect(
                    contents=task.detail_title or task.text,
                    destinationname=task.identifier,
                    Rect=rect,
                    relative=0,
                    thickness=0,
                )

        if detail_tasks:
            pdf_canvas.showPage()

        for index, task in enumerate(detail_tasks):
            pdf_canvas.setPageSize((self.width, self.height))
            pdf_canvas.bookmarkPage(task.identifier)
            pdf_canvas.addOutlineEntry(
                task.detail_title or task.text, task.identifier, level=1, closed=False
            )

            header_bottom = self.__draw_pdf_header_block(
                pdf_canvas,
                self.header,
                heading_font_name,
                fonts_map.get("timeline", body_font_name),
            )
            heading_y = header_bottom - 40
            heading_text = task.detail_title or task.text
            pdf_canvas.setFont(heading_font_name, 20)
            pdf_canvas.setFillColor(colors.black)
            pdf_canvas.drawString(40, heading_y, heading_text)

            body_text = task.detail_body or "No additional detail supplied for this item."
            next_body_y = heading_y - 32
            task_tags = list(getattr(task, "tags", []))
            if task_tags:
                next_body_y = draw_tag_chips(
                    task_tags,
                    start_x=40,
                    start_y=heading_y - 14,
                    max_x=self.width - 40,
                    font_name=body_font_name,
                    font_size=10,
                )

            text_object = pdf_canvas.beginText(40, next_body_y)
            text_object.setFont(body_font_name, 12)
            text_object.setLeading(16)
            wrapped_lines = simpleSplit(body_text, body_font_name, 12, self.width - 80)
            for line in wrapped_lines:
                text_object.textLine(line)
            pdf_canvas.drawText(text_object)
            current_y = text_object.getY()

            outline_start_y = current_y - 20
            nested_overview = nested_artifacts.get(task.identifier)
            if nested_overview and nested_overview.groups:
                pdf_canvas.setFont(heading_font_name, 12)
                pdf_canvas.setFillColor(colors.black)
                pdf_canvas.drawString(40, outline_start_y, "Roadmap Tasks")
                outline_y = outline_start_y - 16
                pdf_canvas.setFont(body_font_name, 11)
                text_width_limit = self.width - 80

                for group in nested_overview.groups:
                    pdf_canvas.drawString(40, outline_y, f"{group.text}:")
                    outline_y -= 14
                    for subtask in group.tasks:
                        pdf_canvas.drawString(
                            60,
                            outline_y,
                            f"- {subtask.text} ({subtask.start} to {subtask.end})",
                        )
                        outline_y -= 12
                        subtask_tags = list(getattr(subtask, "tags", []))
                        if subtask_tags:
                            outline_y = draw_tag_chips(
                                subtask_tags,
                                start_x=70,
                                start_y=outline_y,
                                max_x=self.width - 40,
                                font_name=body_font_name,
                                font_size=9,
                            )
                            pdf_canvas.setFont(body_font_name, 11)
                        if getattr(subtask, "detail_body", None):
                            detail_lines = simpleSplit(
                                subtask.detail_body,
                                body_font_name,
                                10,
                                text_width_limit - 60,
                            )
                            pdf_canvas.setFont(body_font_name, 10)
                            for line in detail_lines:
                                pdf_canvas.drawString(70, outline_y, line)
                                outline_y -= 12
                            pdf_canvas.setFont(body_font_name, 11)
                        if subtask.milestones:
                            pdf_canvas.drawString(70, outline_y, "Milestones:")
                            outline_y -= 12
                            for milestone in subtask.milestones:
                                pdf_canvas.drawString(
                                    80,
                                    outline_y,
                                    f"• {milestone.text} ({milestone.date})",
                                )
                                outline_y -= 12
                        for parallel_task in subtask.tasks:
                            pdf_canvas.drawString(
                                70,
                                outline_y,
                                f"* {parallel_task.text} ({parallel_task.start} to {parallel_task.end})",
                            )
                            outline_y -= 12
                            parallel_tags = list(getattr(parallel_task, "tags", []))
                            if parallel_tags:
                                outline_y = draw_tag_chips(
                                    parallel_tags,
                                    start_x=90,
                                    start_y=outline_y,
                                    max_x=self.width - 40,
                                    font_name=body_font_name,
                                    font_size=8,
                                )
                                pdf_canvas.setFont(body_font_name, 11)
                            if getattr(parallel_task, "detail_body", None):
                                pdf_canvas.setFont(body_font_name, 10)
                                for line in simpleSplit(
                                    parallel_task.detail_body,
                                    body_font_name,
                                    10,
                                    text_width_limit - 80,
                                ):
                                    pdf_canvas.drawString(90, outline_y, line)
                                    outline_y -= 12
                                pdf_canvas.setFont(body_font_name, 11)
                            if parallel_task.milestones:
                                pdf_canvas.drawString(90, outline_y, "Milestones:")
                                outline_y -= 12
                                for milestone in parallel_task.milestones:
                                    pdf_canvas.drawString(
                                        100,
                                        outline_y,
                                        f"• {milestone.text} ({milestone.date})",
                                    )
                                    outline_y -= 12
                        outline_y -= 6
                    outline_y -= 8
                current_y = outline_y

            if task.detail_links:
                link_y = current_y - 30
                pdf_canvas.setFont(heading_font_name, 12)
                pdf_canvas.drawString(40, link_y, "Related Links")
                link_y -= 20
                pdf_canvas.setFont(body_font_name, 11)
                for label, url in task.detail_links:
                    label_text = label or url
                    pdf_canvas.setFillColor(colors.HexColor("#1f77b4"))
                    pdf_canvas.drawString(40, link_y, label_text)
                    text_width = pdf_canvas.stringWidth(label_text, body_font_name, 11)
                    pdf_canvas.linkURL(
                        url,
                        (40, link_y - 2, 40 + text_width, link_y + 12),
                        relative=0,
                        thickness=0,
                    )
                    pdf_canvas.setFillColor(colors.black)
                    link_y -= 18

            button_height = 28
            button_y = 40
            back_width = 180
            draw_nav_button(
                "Back to overview",
                "roadmap_overview",
                40,
                button_y,
                back_width,
                button_height,
                font_name=heading_font_name,
            )
            if task.identifier in nested_artifacts:
                nested_dest = f"{task.identifier}_roadmap"
                draw_nav_button(
                    "Open detailed roadmap",
                    nested_dest,
                    40 + back_width + 20,
                    button_y,
                    back_width,
                    button_height,
                    font_name=heading_font_name,
                )

            if index < len(detail_tasks) - 1:
                pdf_canvas.showPage()

        for task in detail_tasks:
            nested_roadmap = nested_artifacts.get(task.identifier)
            if nested_roadmap is None:
                continue
            nested_dest = f"{task.identifier}_roadmap"
            pdf_canvas.showPage()
            page_width = float(getattr(nested_roadmap, "width", self.width))
            page_height = float(getattr(nested_roadmap, "height", self.height))
            pdf_canvas.setPageSize((page_width, page_height))
            pdf_canvas.bookmarkPage(nested_dest)
            pdf_canvas.addOutlineEntry(
                f"{nested_roadmap.title.text if nested_roadmap.title else task.detail_title or task.text} Detail",
                nested_dest,
                level=2,
                closed=False,
            )

            nested_fonts_map = nested_roadmap.__collect_font_names()
            nested_font_files = getattr(nested_roadmap, "_font_files", {})

            def nested_ensure(font_name: str) -> str:
                if not font_name:
                    return ensure_pdf_font("Helvetica", "")
                file_path = nested_font_files.get(font_name, "")
                return ensure_pdf_font(font_name, file_path)

            nested_body_font = nested_ensure(
                getattr(
                    nested_roadmap,
                    "_pdf_body_font",
                    nested_fonts_map.get("task", body_font_name),
                )
            )
            nested_fonts_map["body"] = nested_body_font
            nested_heading_font = nested_ensure(
                nested_fonts_map.get("title", nested_body_font)
            )
            nested_fonts_map["title"] = nested_heading_font
            nested_fonts_map["timeline"] = nested_ensure(
                nested_fonts_map.get("timeline", nested_body_font)
            )
            nested_fonts_map["group"] = nested_ensure(
                nested_fonts_map.get("group", nested_body_font)
            )
            nested_fonts_map["task"] = nested_ensure(
                nested_fonts_map.get("task", nested_body_font)
            )
            nested_fonts_map["milestone"] = nested_ensure(
                nested_fonts_map.get("milestone", nested_body_font)
            )
            if nested_roadmap.marker is not None:
                nested_fonts_map["marker"] = nested_ensure(
                    nested_roadmap.marker.font
                )
            else:
                nested_fonts_map["marker"] = nested_fonts_map["timeline"]

            nested_roadmap.__draw_on_canvas(
                pdf_canvas, nested_fonts_map, nested_body_font, nested_heading_font
            )
            button_height = 28
            button_y = 40
            button_width = 180
            draw_nav_button(
                "Back to detail",
                task.identifier,
                40,
                button_y,
                button_width,
                button_height,
                font_name=heading_font_name,
            )
            draw_nav_button(
                "Back to overview",
                "roadmap_overview",
                40 + button_width + 20,
                button_y,
                button_width,
                button_height,
                font_name=heading_font_name,
            )

        pdf_canvas.save()

    def save(self, filename: str) -> None:
        """Persist the rendered roadmap to disk.

        Args:
            filename (str): Target file name. Supports PNG and interactive PDF outputs.
        """
        output_path = Path(filename)
        if output_path.suffix.lower() == ".pdf":
            self.__save_pdf(output_path)
        else:
            self.__painter.save_surface(str(output_path))

    def print_roadmap(self, print_area: str = "all") -> None:
        """Print the content of the roadmap

        Args:
            print_area (str, optional): Roadmap area to print. Defaults to "all". Options are "all", "title", "timeline", "groups", "footer"
        """
        dash = "─"
        space = " "
        if print_area == "all" or print_area == "title":
            print(f"Title={self.title.text}")

        if print_area == "all" or print_area == "timeline":
            print("Timeline:")
            for timeline_item in self.timeline.timeline_items:
                print(
                    f"└{dash*8}{timeline_item.text}, value={timeline_item.value}, "
                    f"box_x={round(timeline_item.box_x,2)}, box_y={timeline_item.box_y}, "
                    f"box_w={round(timeline_item.box_width,2)}, box_h={timeline_item.box_height}, "
                    f"text_x={round(timeline_item.text_x,2)}, text_y={timeline_item.text_y}"
                )

        if print_area == "all" or print_area == "groups":
            for group in self.groups:
                print(
                    f"Group: text={group.text}, x={round(group.box_x, 2)}, y={group.box_y},",
                    f"w={group.box_width}, h={group.box_height}",
                )
                for task in group.tasks:
                    print(
                        f"└{dash*8}{task.text}, start={task.start}, end={task.end}, "
                        f"x={round(task.box_x, 2)}, y={task.box_y}, w={round(task.box_width, 2)}, "
                        f"h={task.box_height}"
                    )
                    for milestone in task.milestones:
                        print(
                            f"{space*9}├{dash*4}{milestone.text}, date={milestone.date}, x={round(milestone.diamond_x, 2)}, "
                            f"y={milestone.diamond_y}, w={milestone.diamond_width}, h={milestone.diamond_height}, "
                            f"font_colour={milestone.font_colour}, fill_colour={milestone.fill_colour}"
                        )
                    for parellel_task in task.tasks:
                        print(
                            f"{space*9}└{dash*4}Parellel Task: {parellel_task.text}, start={parellel_task.start}, "
                            f"end={parellel_task.end}, x={round(parellel_task.box_x,2)}, y={round(parellel_task.box_y, 2)}, "
                            f"w={round(parellel_task.box_width, 2)}, h={round(parellel_task.box_height,2)}"
                        )
                        for parellel_task_milestone in parellel_task.milestones:
                            print(
                                f"{space*14}├{dash*4}{parellel_task_milestone.text}, "
                                f"date={parellel_task_milestone.date}, x={round(parellel_task_milestone.diamond_x, 2)}, "
                                f"y={round(parellel_task_milestone.diamond_y, 2)}, w={parellel_task_milestone.diamond_width}, "
                                f"h={parellel_task_milestone.diamond_height}"
                            )
        if print_area == "all" or print_area == "footer":
            if self.footer != None:
                print(
                    f"Footer: {self.footer.text} x={self.footer.x} "
                    f"y={self.footer.y} w={self.footer.width} "
                    f"h={self.footer.height}"
                )
