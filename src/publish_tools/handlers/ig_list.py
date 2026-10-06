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
                if edition.package == info.package and edition.url == info.path:
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


def package_families(package_ids):
    """
    Map each package ID to its family prefix.

    Use the shortest shared prefix that is an existing package ID or branches
    into multiple namespaces with at least three components. Packages without
    a qualifying shared prefix retain their full ID as the family name.
    """
    package_ids = set(package_ids)
    children, members = {}, {}
    for package_id in package_ids:
        parts = package_id.split(".")
        for length in range(1, len(parts) + 1):
            prefix = ".".join(parts[:length])
            members.setdefault(prefix, set()).add(package_id)
            if length < len(parts):
                children.setdefault(prefix, set()).add(parts[length])
    return {package_id: next((prefix
            for length in range(1, len(package_id.split(".")) + 1)
            if (prefix := ".".join(package_id.split(".")[:length]))
            and len(members[prefix]) > 1
            and (prefix in package_ids or
                 (length >= 3 and len(children.get(prefix, ())) > 1))), package_id)
            for package_id in package_ids}


def render(registry_dir: Path, ig_list: IgList | None = None):
    if ig_list is None and (ig_list := read(registry_dir, FILE_NAME, IgList)) is None:
        ig_list = IgList()

    packages = {}
    for guide in ig_list.guides:
        package = packages.setdefault(guide.npm_name, {
            "name": guide.name, "package_id": guide.npm_name, "editions": {},
        })
        for edition in guide.editions:
            package["editions"][(edition.package, str(edition.url))] = edition

    families = package_families(packages)
    data = {"title": "IG List", "groups": {}}
    for package_id, package in sorted(packages.items()):
        channels = {}
        for edition in package.pop("editions").values():
            channel = release_channel(edition.ig_version, edition.name)
            releases = channels.setdefault(channel, {})
            release = releases.setdefault(edition.ig_version, {
                "version": edition.ig_version, "igs": [],
            })
            release["igs"].append(edition)
        for releases in channels.values():
            for release in releases.values():
                release["igs"].sort(key=lambda edition: (edition.name.casefold(), str(edition.url)))

        stable = sorted(channels.get("Veröffentlichungen", {}).values(),
                        key=lambda release: version_key(release["version"]), reverse=True)
        latest = stable[0] if stable else None
        package["latest"] = latest
        package["older"] = stable[1:]
        package["previews"] = []
        for name in ("Ballot", "Release Candidate"):
            previews = sorted(channels.get(name, {}).values(),
                              key=lambda release: version_key(release["version"]), reverse=True)
            if previews:
                visible = previews[:1]
                package["previews"].append({
                    "name": name, "visible": visible,
                    "older": [release for release in previews if release not in visible],
                })
        data["groups"].setdefault(families[package_id], []).append(package)

    render_helper(registry_dir, RENDER_FILE_NAME, data, "ig_list.jinja")
    log.succ("rendered ig list")
