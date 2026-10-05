from pathlib import Path

from .. import log
from ..models.guide import Guide
from ..models.ig_info import IgInfo, IgInfoFirst
from ..models.ig_list import IgList
from .helper import read, release_channel, version_key
from .helper import render as render_helper
from .helper import write

FILE_NAME = "ig_list.json"
RENDER_FILE_NAME = "index.html"


def update(ig_registry_dir: Path, info: IgInfo | IgInfoFirst) -> IgList:
    """
    Update the IG List file
    """
    if (ig_list := read(ig_registry_dir, FILE_NAME, IgList)) is None:
        ig_list = IgList()

    # Check guides if entry already exists
    guide_found = False
    for guide in ig_list.guides:
        if guide.npm_name == info.package_id:

            edition_found = False
            for i, edition in enumerate(guide.editions):
                if edition.package == info.package:
                    guide.editions[i] = info.edition
                    edition_found = True
                    break

            if not edition_found:
                guide.editions.append(info.edition)

            guide_found = True
            break

    # If guide does not exists, add as new one
    if not guide_found:
        if not isinstance(info, IgInfoFirst):
            raise Exception("Guide does not exist but is not first release")

        guide = Guide(
            name=info.title,
            category=info.category,
            npm_name=info.package_id,
            description=info.introduction,
            canonical=info.canonical,
            ci_build=info.ci_build,
            editions=[info.edition],
        )
        ig_list.guides.append(guide)

    write(ig_registry_dir, FILE_NAME, ig_list)
    log.succ(f"updated ig list {ig_registry_dir/FILE_NAME}")

    return ig_list


def render(registry_dir: Path, ig_list: IgList | None = None):
    if ig_list is None and (ig_list := read(registry_dir, FILE_NAME, IgList)) is None:
        ig_list = IgList()

    packages = {}
    for guide in ig_list.guides:
        package = packages.setdefault(guide.npm_name, {
            "name": guide.name, "package_id": guide.npm_name, "editions": {},
        })
        for edition in guide.editions:
            package["editions"][edition.package] = edition

    data = {"title": "IG List", "packages": []}
    for package_id, package in sorted(packages.items()):
        editions = sorted(package.pop("editions").values(),
                          key=lambda edition: version_key(edition.ig_version), reverse=True)
        stable = [edition for edition in editions if
                  release_channel(edition.ig_version, edition.name, edition.status or "") == "Veröffentlichungen"]
        latest = stable[0] if stable else None
        package["latest"] = latest
        package["older"] = stable[1:]
        package["previews"] = []
        for name in ("Ballot", "Release Candidate"):
            previews = [edition for edition in editions if
                        release_channel(edition.ig_version, edition.name, edition.status or "") == name]
            if previews:
                visible = [edition for index, edition in enumerate(previews)
                           if index == 0 or (name == "Ballot" and latest and latest.date
                                             and edition.date and edition.date < latest.date)]
                package["previews"].append({
                    "name": name, "visible": visible,
                    "older": [edition for edition in previews if edition not in visible],
                })
        data["packages"].append(package)

    render_helper(registry_dir, RENDER_FILE_NAME, data, "ig_list.jinja")
    log.succ("rendered ig list")
