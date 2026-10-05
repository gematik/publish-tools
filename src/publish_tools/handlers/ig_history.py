from pathlib import Path

from .. import log
from ..models.package_list import PackageList
from .helper import render as render_helper
from .helper import release_channel, version_key

FILE_NAME = "ig_history.json"
RENDER_FILE_NAME = "index.html"


def render(ig_dir: Path, plist: PackageList):
    data = {
        "title": plist.title,
        "introduction": plist.introduction,
    }

    data["channels"] = []
    data["ci_builds"] = [entry for entry in plist.list if not hasattr(entry, "sequence")]
    releases = [entry for entry in plist.list if hasattr(entry, "sequence")]
    for name in ("Veröffentlichungen", "Ballot", "Release Candidate"):
        entries = sorted(
            [entry for entry in releases
             if release_channel(entry.version, entry.sequence, entry.status.value) == name],
            key=lambda entry: (entry.current, version_key(entry.version), entry.date),
            reverse=True,
        )
        if entries:
            data["channels"].append({
                "name": name, "latest": entries[0], "older": entries[1:],
            })

    render_helper(ig_dir, RENDER_FILE_NAME, data, "history.jinja")
    log.succ("rendered ig history")
