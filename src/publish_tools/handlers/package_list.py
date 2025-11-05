from pathlib import Path

from .. import log
from ..models.ig_info import IgInfo
from ..models.package_list import (
    PackageList,
    PackageListCiBuildEntry,
    PackageListSpecificEntry,
)
from ..models.sushi_config import SushiConfigReleaseLabel

FILE_NAME = "package_list.json"

CI_VERSION_DESCRIPTION = "Continuous Integration Build (latest in version control)"


def update(ig_dir: Path, info: IgInfo) -> Path:
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

    file = ig_dir / FILE_NAME
    if plist := read(file):
        entry_found = False
        for i, pl_entry in enumerate(plist.list):
            if pl_entry.version == info.version:
                plist.list[i] = entry
                entry_found = True
                break

        if not entry_found:
            plist.list.append(entry)

    else:
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

    write(file, plist)
    log.succ("created/updated package list")

    return file


def read(file: Path) -> PackageList | None:
    if not file.exists():
        return None

    content = file.read_text(encoding="utf-8")
    return PackageList.model_validate_json(content)


def write(file: Path, plist: PackageList) -> None:
    content = plist.model_dump_json(indent=4, by_alias=True)
    file.write_text(content, encoding="utf-8")
