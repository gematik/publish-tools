from pathlib import Path

from .. import log
from ..models.release_channel import ReleaseChannel
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

    builds = [entry for entry in plist.list if not hasattr(entry, "sequence")]
    releases = sorted(
        [entry for entry in plist.list if hasattr(entry, "sequence")],
        key=lambda entry: (entry.date, version_key(entry.version)),
        reverse=True,
    )
    stable = [
        entry
        for entry in releases
        if release_channel(entry.version, entry.sequence, entry.status.value)
        == ReleaseChannel.STABLE
    ]
    current = stable[:1]
    data["current_entries"] = current + builds
    data["channels"] = []
    for name in (
        ReleaseChannel.STABLE,
        ReleaseChannel.RELEASE_CANDIDATE,
        ReleaseChannel.BALLOT,
    ):
        entries = [
            entry
            for entry in releases
            if release_channel(entry.version, entry.sequence, entry.status.value)
            == name
        ]
        if not entries:
            continue
        sequences = {}
        for entry in entries:
            sequences.setdefault(entry.sequence, []).append(entry)
        data["channels"].append(
            {
                "name": name,
                "current": [entry for entry in current if entry in entries],
                "sequences": sequences,
                "current_sequences": {
                    entry.sequence for entry in current if entry in entries
                },
            }
        )
    data["release_channel"] = release_channel
    data["ReleaseChannel"] = ReleaseChannel

    render_helper(ig_dir, RENDER_FILE_NAME, data, "history.jinja")
    log.succ("rendered ig history")
