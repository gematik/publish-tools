from pathlib import Path

from .. import log
from ..models.guide import Guide
from ..models.ig_info import IgInfo
from .helper import render as render_helper

FILE_NAME = "ig_history.json"
RENDER_FILE_NAME = "index.html"


def update(ig_dir: Path, info: IgInfo) -> Path:
    ig_dir.mkdir(parents=True, exist_ok=True)

    ig_history_file = ig_dir / FILE_NAME
    if ig_history_file.exists():
        content = ig_history_file.read_text(encoding="utf-8")
        guide = Guide.model_validate_json(content)

        edition_found = False
        for i, edition in enumerate(guide.editions):
            if edition.package == info.package:
                guide.editions[i] = edition
                edition_found = True
                break

        if not edition_found:
            guide.editions.append(info.edition)

    else:
        guide = Guide.model_validate(
            {
                "editions": [info.edition],
                **info.model_dump(),
            }
        )

    content = guide.model_dump_json(indent=4, by_alias=True)
    ig_history_file.write_text(content, encoding="utf-8")

    log.succ("created/updated history file")

    return ig_history_file


def render(file: Path):
    content = file.read_text(encoding="utf-8")
    history = Guide.model_validate_json(content)

    data = history.model_dump()

    # Create sequences
    data["sequences"] = {}
    # Handle sequences
    for edition in history.editions:
        if edition.name not in data["sequences"]:
            data["sequences"][edition.name] = []
        data["sequences"][edition.name].append(edition)

    content = render_helper(data, "history.jinja")

    output = file.with_name(RENDER_FILE_NAME)
    output.write_text(content, encoding="utf-8")
    log.succ("rendered ig history")
