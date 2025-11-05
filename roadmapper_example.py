from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

import yaml

from roadmapper.roadmap import Roadmap
from roadmapper.timelinemode import TimelineMode

CONFIG_PATH = Path(__file__).with_name("roadmap_config.yaml")


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def timeline_mode_from_string(value: str) -> TimelineMode:
    lookup = value.upper().replace("-", "_")
    mapping = {
        "WEEKLY": TimelineMode.WEEKLY,
        "MONTHLY": TimelineMode.MONTHLY,
        "QUARTERLY": TimelineMode.QUARTERLY,
        "HALF_YEARLY": TimelineMode.HALF_YEARLY,
        "HALF_YEAR": TimelineMode.HALF_YEARLY,
        "YEARLY": TimelineMode.YEARLY,
        "ANNUAL": TimelineMode.YEARLY,
    }
    try:
        return mapping[lookup]
    except KeyError as exc:
        raise ValueError(f"Unsupported timeline mode '{value}'.") from exc


def months_between(start_str: str, end_str: str) -> int:
    start_dt = datetime.strptime(start_str, "%Y-%m-%d")
    end_dt = datetime.strptime(end_str, "%Y-%m-%d")
    months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month) + 1
    return max(months, 1)


def default_timeline_items(start: str, end: str, mode: TimelineMode) -> int:
    months = months_between(start, end)
    if mode == TimelineMode.QUARTERLY:
        return max(1, (months + 2) // 3)
    if mode == TimelineMode.WEEKLY:
        weeks = max(1, round((months * 30) / 7))
        return min(26, weeks)
    return max(3, min(months, 18))


def normalise_tag_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if item]
    return []


def resolved_task_tags(task_cfg: dict[str, Any], fallback: list[str]) -> list[str]:
    tags = normalise_tag_list(task_cfg.get("tags"))
    if tags:
        return tags
    return [tag for tag in fallback if tag]


def apply_tag_styles(
    roadmap: Roadmap,
    base_cfg: Optional[dict[str, Any]],
    override_cfg: Optional[dict[str, Any]] = None,
) -> None:
    palette: dict[str, str] = {}
    defaults: Optional[list[str]] = None

    def extract(config: Optional[dict[str, Any]]) -> None:
        nonlocal palette, defaults
        if not config:
            return
        tag_cfg = config.get("tags")
        if not isinstance(tag_cfg, dict):
            return
        palette_cfg = tag_cfg.get("palette")
        if isinstance(palette_cfg, dict):
            palette.update(
                {
                    str(tag): str(colour)
                    for tag, colour in palette_cfg.items()
                    if tag and colour
                }
            )
        default_cfg = tag_cfg.get("defaults")
        if isinstance(default_cfg, (list, tuple)) and default_cfg:
            defaults = [str(colour) for colour in default_cfg if colour]

    extract(base_cfg)
    extract(override_cfg)
    roadmap.set_tag_styles(palette or None, defaults)


def build_default_detail_text(task_cfg: dict[str, Any], area_name: str) -> str:
    milestone = next(iter(task_cfg.get("milestones", [])), None)
    milestone_name = milestone["name"] if milestone else "Milestone"
    milestone_date = milestone["date"] if milestone else task_cfg["end"]
    return (
        f"{task_cfg['name']} anchors the {area_name} workstream.\n"
        f"Window: {task_cfg['start']} -> {task_cfg['end']}\n"
        f"Milestone target: {milestone_name} ({milestone_date}).\n\n"
        "Key alignment questions:\n"
        "- What success signals prove completion?\n"
        "- Which dependencies must land early?\n"
        "- Who owns stakeholder updates?"
    )


def apply_fonts(
    roadmap: Roadmap,
    base_fonts: Optional[dict[str, Any]],
    override_fonts: Optional[dict[str, Any]] = None,
) -> None:
    def parse_font_entry(entry: Any) -> tuple[str, Optional[str]]:
        if isinstance(entry, dict):
            return entry.get("name", ""), entry.get("file")
        if isinstance(entry, str):
            return entry, None
        return "", None

    base_fonts = base_fonts or {}
    component_fonts: dict[str, str] = {}
    font_files: dict[str, str] = {}

    family_entry = base_fonts.get("family")
    family, family_file = parse_font_entry(family_entry)
    if family_file:
        font_files[family] = str(resolve_path(family_file))

    components_cfg = base_fonts.get("components", {}) or {}
    for component, entry in components_cfg.items():
        font_name, font_file = parse_font_entry(entry)
        if font_name:
            component_fonts[component] = font_name
        if font_name and font_file:
            font_files[font_name] = str(resolve_path(font_file))

    pdf_options: dict[str, Any] = {}
    if base_fonts.get("pdf"):
        if isinstance(base_fonts["pdf"], dict):
            pdf_options.update(base_fonts["pdf"])
        else:
            pdf_options["name"] = base_fonts["pdf"]

    if override_fonts:
        override_family_entry = override_fonts.get("family")
        if override_family_entry is not None:
            override_family, override_file = parse_font_entry(override_family_entry)
            if override_family:
                family = override_family
            if override_family and override_file:
                font_files[override_family] = str(resolve_path(override_file))

        component_override = override_fonts.get("components") or {}
        for component, entry in component_override.items():
            font_name, font_file = parse_font_entry(entry)
            if font_name:
                component_fonts[component] = font_name
            if font_name and font_file:
                font_files[font_name] = str(resolve_path(font_file))

        override_pdf = override_fonts.get("pdf")
        if override_pdf:
            if isinstance(override_pdf, dict):
                pdf_options.update(override_pdf)
            else:
                pdf_options["name"] = override_pdf

    pdf_name = pdf_options.get("name", family)
    pdf_file = pdf_options.get("file")
    if pdf_file:
        pdf_file = str(resolve_path(pdf_file))

    if not family and not component_fonts and not pdf_name and not pdf_file:
        return

    roadmap.set_fonts(
        family=family,
        component_fonts=component_fonts or None,
        pdf_font_name=pdf_name or "",
        pdf_font_file=pdf_file or "",
        font_files=font_files or None,
    )


def resolve_path(value: Optional[str]) -> Optional[Path]:
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = (CONFIG_PATH.parent / path).resolve()
    return path


def create_detail_roadmap_builder(
    root_config: dict[str, Any],
    area_cfg: dict[str, Any],
    task_cfg: dict[str, Any],
    roadmap_cfg: dict[str, Any],
) -> Callable[[], Roadmap]:
    def builder() -> Roadmap:
        nested = Roadmap(
            roadmap_cfg.get("width", root_config.get("width", 1400)),
            roadmap_cfg.get("height", root_config.get("height", 750)),
            colour_theme=roadmap_cfg.get(
                "colour_theme", root_config.get("colour_theme", "DEFAULT")
            ),
        )
        apply_fonts(nested, root_config.get("fonts"), roadmap_cfg.get("fonts"))
        apply_tag_styles(nested, root_config, roadmap_cfg)

        header_cfg = roadmap_cfg.get("header")
        nested_title = roadmap_cfg.get("title", f"{task_cfg['name']} Detailed Roadmap")
        nested_subtitle = roadmap_cfg.get("subtitle", area_cfg.get("name"))
        if header_cfg:
            nested.set_header(
                logo_path=str(resolve_path(header_cfg.get("logo"))),
                logo_width=header_cfg.get("logo_width", 80),
                logo_height=header_cfg.get("logo_height", 80),
                background_colour=header_cfg.get("background", "#FFFFFF"),
                divider_colour=header_cfg.get("divider", "#CCCCCC"),
                padding_x=header_cfg.get("padding_x", 24),
                padding_y=header_cfg.get("padding_y", 18),
                logo_spacing=header_cfg.get("logo_spacing", 16),
                title=header_cfg.get("title", nested_title),
                subtitle=header_cfg.get("subtitle", nested_subtitle),
            )
        else:
            nested.set_title(nested_title)
            if nested_subtitle:
                nested.set_subtitle(nested_subtitle)

        timeline_cfg = roadmap_cfg.get("timeline", {})
        timeline_mode = timeline_mode_from_string(
            timeline_cfg.get(
                "mode",
                root_config.get("timeline", {}).get("mode", "MONTHLY"),
            )
        )
        timeline_start = timeline_cfg.get("start", task_cfg["start"])
        timeline_items = timeline_cfg.get("items")
        if timeline_items is None:
            timeline_items = default_timeline_items(
                task_cfg["start"], task_cfg["end"], timeline_mode
            )
        nested.set_timeline(
            timeline_mode,
            start=timeline_start,
            number_of_items=int(timeline_items),
        )

        for group_cfg in roadmap_cfg.get("groups", []):
            nested_group = nested.add_group(group_cfg.get("name", "Workstream"))
            for nested_task_cfg in group_cfg.get("tasks", []):
                nested_task = nested_group.add_task(
                    nested_task_cfg["name"],
                    nested_task_cfg["start"],
                    nested_task_cfg["end"],
                    tags=resolved_task_tags(
                        nested_task_cfg, [nested_group.text]
                    ),
                )
                for milestone_cfg in nested_task_cfg.get("milestones", []):
                    nested_task.add_milestone(
                        milestone_cfg["name"],
                        milestone_cfg["date"],
                    )
                detail_cfg = nested_task_cfg.get("detail")
                if detail_cfg:
                    if isinstance(detail_cfg, dict):
                        body = detail_cfg.get("description") or ""
                        title_override = detail_cfg.get("title")
                        if body:
                            nested_task.set_detail(body, title=title_override)
                        for link_cfg in detail_cfg.get("links", []):
                            label = link_cfg.get("label") or link_cfg.get("url")
                            url = link_cfg.get("url")
                            if label and url:
                                nested_task.add_detail_link(label, url)
                    elif isinstance(detail_cfg, str):
                        nested_task.set_detail(detail_cfg)
                elif nested_task_cfg.get("detail"):
                    nested_task.set_detail(str(nested_task_cfg["detail"]))

        footer_text = roadmap_cfg.get("footer", root_config.get("footer"))
        if footer_text:
            nested.set_footer(footer_text)

        return nested

    return builder


def build_roadmap_from_definition(
    definition: dict[str, Any], root_config: dict[str, Any]
) -> Roadmap:
    roadmap = Roadmap(
        definition.get("width", root_config.get("width", 1400)),
        definition.get("height", root_config.get("height", 750)),
        colour_theme=definition.get(
            "colour_theme", root_config.get("colour_theme", "DEFAULT")
        ),
    )

    apply_fonts(roadmap, root_config.get("fonts"), definition.get("fonts"))
    apply_tag_styles(roadmap, root_config, definition)

    title_text = definition.get("title", root_config.get("title", "Roadmap"))
    subtitle_text = definition.get("subtitle", root_config.get("subtitle"))
    header_cfg = definition.get("header")
    if header_cfg:
        roadmap.set_header(
            logo_path=str(resolve_path(header_cfg.get("logo"))),
            logo_width=header_cfg.get("logo_width", 80),
            logo_height=header_cfg.get("logo_height", 80),
            background_colour=header_cfg.get("background", "#FFFFFF"),
            divider_colour=header_cfg.get("divider", "#CCCCCC"),
            padding_x=header_cfg.get("padding_x", 24),
            padding_y=header_cfg.get("padding_y", 18),
            logo_spacing=header_cfg.get("logo_spacing", 16),
            title=header_cfg.get("title", title_text),
            subtitle=header_cfg.get("subtitle", subtitle_text),
        )
    else:
        fallback_header = root_config.get("header")
        if fallback_header:
            roadmap.set_header(
                logo_path=str(resolve_path(fallback_header.get("logo"))),
                logo_width=fallback_header.get("logo_width", 80),
                logo_height=fallback_header.get("logo_height", 80),
                background_colour=fallback_header.get("background", "#FFFFFF"),
                divider_colour=fallback_header.get("divider", "#CCCCCC"),
                padding_x=fallback_header.get("padding_x", 24),
                padding_y=fallback_header.get("padding_y", 18),
                logo_spacing=fallback_header.get("logo_spacing", 16),
                title=title_text,
                subtitle=subtitle_text,
            )
        else:
            roadmap.set_title(title_text)
            if subtitle_text:
                roadmap.set_subtitle(subtitle_text)

    timeline_cfg = definition.get("timeline", {})
    base_timeline = root_config.get("timeline", {})
    roadmap.set_timeline(
        timeline_mode_from_string(
            timeline_cfg.get("mode", base_timeline.get("mode", "MONTHLY"))
        ),
        start=timeline_cfg.get("start", base_timeline.get("start", "2025-01-01")),
        number_of_items=timeline_cfg.get("items", base_timeline.get("items", 12)),
        show_generic_dates=timeline_cfg.get(
            "show_generic_dates", base_timeline.get("show_generic_dates", False)
        ),
        font=timeline_cfg.get("font", ""),
        font_size=timeline_cfg.get("font_size", 0),
        font_colour=timeline_cfg.get("font_colour", ""),
        fill_colour=timeline_cfg.get("fill_colour", ""),
    )

    for area_cfg in definition.get("areas", []):
        group = roadmap.add_group(area_cfg["name"])
        for task_cfg in area_cfg.get("tasks", []):
            task = group.add_task(
                task_cfg["name"],
                task_cfg["start"],
                task_cfg["end"],
                tags=resolved_task_tags(task_cfg, [group.text]),
            )
            for milestone_cfg in task_cfg.get("milestones", []):
                task.add_milestone(milestone_cfg["name"], milestone_cfg["date"])

            detail_cfg = task_cfg.get("detail", {})
            if isinstance(detail_cfg, dict):
                detail_text = detail_cfg.get("description") or build_default_detail_text(
                    task_cfg, area_cfg["name"]
                )
                detail_title = detail_cfg.get("title")
                task.set_detail(detail_text, title=detail_title)
                for link_cfg in detail_cfg.get("links", []):
                    label = link_cfg.get("label") or link_cfg.get("url")
                    url = link_cfg.get("url")
                    if label and url:
                        task.add_detail_link(label, url)
                roadmap_cfg = detail_cfg.get("roadmap")
                if roadmap_cfg:
                    task.set_detail_roadmap(
                        create_detail_roadmap_builder(
                            root_config,
                            area_cfg,
                            task_cfg,
                            roadmap_cfg,
                        )
                    )
            elif detail_cfg:
                task.set_detail(str(detail_cfg))
            else:
                task.set_detail(build_default_detail_text(task_cfg, area_cfg["name"]))

    footer = definition.get("footer", root_config.get("footer"))
    if footer:
        roadmap.set_footer(footer)

    return roadmap

def build_primary_roadmap(config: dict[str, Any]) -> Roadmap:
    roadmap = Roadmap(
        config.get("width", 1400),
        config.get("height", 750),
        colour_theme=config.get("colour_theme", "DEFAULT"),
    )

    apply_fonts(roadmap, config.get("fonts"))
    apply_tag_styles(roadmap, config)

    header_cfg = config.get("header")
    title_text = config.get("title", "Roadmap Overview")
    subtitle_text = config.get("subtitle")
    if header_cfg:
        roadmap.set_header(
            logo_path=str(resolve_path(header_cfg.get("logo"))),
            logo_width=header_cfg.get("logo_width", 80),
            logo_height=header_cfg.get("logo_height", 80),
            background_colour=header_cfg.get("background", "#FFFFFF"),
            divider_colour=header_cfg.get("divider", "#CCCCCC"),
            padding_x=header_cfg.get("padding_x", 24),
            padding_y=header_cfg.get("padding_y", 18),
            logo_spacing=header_cfg.get("logo_spacing", 16),
            title=header_cfg.get("title", title_text),
            subtitle=header_cfg.get("subtitle", subtitle_text),
        )
    else:
        roadmap.set_title(title_text)
        if subtitle_text:
            roadmap.set_subtitle(subtitle_text)

    timeline_cfg = config.get("timeline", {})
    roadmap.set_timeline(
        timeline_mode_from_string(timeline_cfg.get("mode", "MONTHLY")),
        start=timeline_cfg.get(
            "start", datetime.strftime(datetime.today(), "%Y-%m-%d")
        ),
        number_of_items=timeline_cfg.get("items", 12),
    )

    for area_cfg in config.get("areas", []):
        group = roadmap.add_group(area_cfg["name"])
        for task_cfg in area_cfg.get("tasks", []):
            task = group.add_task(
                task_cfg["name"],
                task_cfg["start"],
                task_cfg["end"],
                tags=resolved_task_tags(task_cfg, [group.text]),
            )
            for milestone_cfg in task_cfg.get("milestones", []):
                task.add_milestone(milestone_cfg["name"], milestone_cfg["date"])

            detail_cfg = task_cfg.get("detail", {})
            detail_text = detail_cfg.get("description") or build_default_detail_text(
                task_cfg, area_cfg["name"]
            )
            detail_title = detail_cfg.get("title")
            task.set_detail(detail_text, title=detail_title)

            for link_cfg in detail_cfg.get("links", []):
                label = link_cfg.get("label") or link_cfg.get("url")
                url = link_cfg.get("url")
                if label and url:
                    task.add_detail_link(label, url)

            roadmap_cfg = detail_cfg.get("roadmap")
            if roadmap_cfg:
                task.set_detail_roadmap(
                    create_detail_roadmap_builder(
                        config,
                        area_cfg,
                        task_cfg,
                        roadmap_cfg,
                    )
                )

    footer = config.get("footer")
    if footer:
        roadmap.set_footer(footer)

    return roadmap


def main() -> None:
    config = load_config()
    roadmap = build_primary_roadmap(config)
    roadmap.draw()
    roadmap.save("enterprise_transformation_roadmap.png")
    roadmap.save("enterprise_transformation_roadmap.pdf")


if __name__ == "__main__":
    main()
