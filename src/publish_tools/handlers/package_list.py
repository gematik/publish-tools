import json
from datetime import date
from pathlib import Path

import requests

from .. import log
from ..models.guide import Guide
from ..models.ig_info import IgInfo
from ..models.package_list import (
    PackageList,
    PackageListCiBuildEntry,
    PackageListSpecificEntry,
)
from ..models.sushi_config import SushiConfigReleaseLabel
from .helper import read, write

FILE_NAME = "package-list.json"

CI_VERSION_DESCRIPTION = "Continuous Integration Build (latest in version control)"


def update(ig_dir: Path, info: IgInfo) -> PackageList:
    ig_dir.mkdir(parents=True, exist_ok=True)

    entry = PackageListSpecificEntry(
        version=info.version,
        date=info.date,
        desc=info.desc,
        path=info.path,
        status=info.release_label,
        sequence=info.sequence,
        fhir_version=info.fhir_version[0],
    )

    if plist := read(ig_dir, FILE_NAME, PackageList):
        entry_found = False
        for i, pl_entry in enumerate(plist.list):
            if pl_entry.version == info.version:
                plist.list[i] = entry
                entry_found = True
                break

        if not entry_found:
            plist.list.append(entry)

    else:
        if info.title is None or info.introduction is None:
            raise Exception(
                "Trying to perform first publish from non-first publication request"
            )

        plist = PackageList(
            package_id=info.package_id,
            canonical=info.canonical,
            title=info.title,
            introduction=info.introduction,
        )

        plist.list.append(entry)

    # Add CI build entry and set current
    if info.ci_build:
        ci_found = False
        for entry in plist.list:
            if entry.status == SushiConfigReleaseLabel.CI_BUILD:
                entry.current = True
                ci_found = True

            # All others do not reflex the latest version
            else:
                entry.current = False

        # If ci build entry was not found, it needs to be added
        if not ci_found:
            ci_entry = PackageListCiBuildEntry(
                desc=CI_VERSION_DESCRIPTION,
                path=info.ci_build,
            )
            plist.list.append(ci_entry)

    # If no ci_build, search for the latest release entry
    else:
        # Cannot contain CI Build entry
        latest_version = sorted(plist.list, key=lambda x: x.date)[-1].version  # type: ignore

        # Set the current flag
        for entry in plist.list:
            entry.current = entry.version == latest_version

    write(ig_dir, FILE_NAME, plist)
    log.succ("created/updated package list")

    # Read additional plist files that are read only
    name_pattern = ig_dir / FILE_NAME

    for file in name_pattern.parent.glob(name_pattern.stem + "*" + name_pattern.suffix):
        # Skip the 'original' file as this was aleady handled
        if file == name_pattern:
            continue

        plist_ = read(file.parent, file.name, PackageList)

        if plist_ is not None:
            # Add entries to list
            plist.list.extend(plist_.list)

    return plist


def from_history(guide: Guide) -> PackageList:
    feed = PackageList(
        package_id=guide.npm_name,
        canonical=guide.canonical,
        title=guide.name,
        introduction=guide.description,
    )

    # Fill actual list
    list_: list[PackageListCiBuildEntry | PackageListSpecificEntry] = []
    for edition in guide.editions:
        # Try to get the original date from the IG resource from the server
        resp = requests.get(
            str(edition.url) + f"/ImplementationGuide-{guide.npm_name}.json"
        )

        ig_dict = json.loads(resp.text) if resp.status_code == 200 else {}
        date_ = date.fromisoformat(d) if (d := ig_dict.get("date")) else date.today()

        # Try to get the status from the online IG
        # Get the list of extensions
        exts = ig_dict.get("definition", {}).get("extension", [])

        # Try to find the extension defining 'releaselabel'
        release_ext = (
            e[0]
            if (
                e := [
                    ext
                    for ext in exts
                    if any(
                        [
                            extext.get("valueCode") == "releaselabel"
                            for extext in ext.get("extension", [])
                        ]
                    )
                ]
            )
            and len(e) == 1
            else {}
        )

        # Get inside the extension the extension that defines the value
        release_value = (
            e[0]
            if (
                e := [
                    ext
                    for ext in release_ext.get("extension", [])
                    if ext.get("url") == "value"
                ]
            )
            and len(e) == 1
            else {}
        )

        # If any was found extract the label otherwise use 'release' as default
        status = (
            SushiConfigReleaseLabel(v)
            if (v := release_value.get("valueString"))
            else SushiConfigReleaseLabel.RELEASE
        )

        # Append entry
        list_.append(
            PackageListSpecificEntry(
                version=edition.ig_version,
                desc=edition.description,
                path=edition.url,
                date=date_,
                sequence=edition.name,
                fhir_version=edition.fhir_version[0],
                status=status,
            )
        )

    feed.list = list_

    return feed
