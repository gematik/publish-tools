from pathlib import Path

from .. import log
from ..models.package_list import PackageList
from .helper import render as render_helper

FILE_NAME = "ig_history.json"
RENDER_FILE_NAME = "index.html"


def render(ig_dir: Path, plist: PackageList):
    data = {
        "title": plist.title,
        "introduction": plist.introduction,
        "sequences": {},
    }

    # Handle sequences
    for entry in plist.list:
        sequence = getattr(entry, "sequence", "Current")
        if sequence not in data["sequences"]:
            data["sequences"][sequence] = []
        data["sequences"][sequence].append(entry)

    render_helper(ig_dir, RENDER_FILE_NAME, data, "history.jinja")
    log.succ("rendered ig history")
