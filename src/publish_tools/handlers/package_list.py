from pathlib import Path

from .. import log
from ..models.ig_info import IgInfo
from ..models.package_list import PackageList, PackageListSpecificEntry

FILE_NAME = "package_list.json"


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
    if file.exists():
        content = file.read_text(encoding="utf-8")
        plist = PackageList.model_validate_json(content)

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

    content = plist.model_dump_json(indent=4, by_alias=True)
    file.write_text(content, encoding="utf-8")

    log.succ("created/updated package list")

    return file
