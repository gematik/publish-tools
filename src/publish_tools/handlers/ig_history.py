from pathlib import Path

from .. import log
from ..models.guide import Guide
from ..models.ig_info import IgInfo
from ..models.package_list import PackageList
from .helper import read
from .helper import render as render_helper
from .helper import write

FILE_NAME = "ig_history.json"
RENDER_FILE_NAME = "index.html"


def update(ig_dir: Path, info: IgInfo) -> Guide:
    if guide := read(ig_dir, FILE_NAME, Guide):
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

    write(ig_dir, FILE_NAME, guide)
    log.succ("created/updated history file")

    return guide


def render(ig_dir: Path, plist: PackageList):
    data = plist.model_dump()

    # Create sequences
    data["sequences"] = {}
    # Handle sequences
    for entry in plist.list:
        sequence = getattr(entry, "sequence", "Current")
        if sequence not in data["sequences"]:
            data["sequences"][sequence] = []
        data["sequences"][sequence].append(entry)

    render_helper(ig_dir, RENDER_FILE_NAME, data, "history.jinja")
    log.succ("rendered ig history")
