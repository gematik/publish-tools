import re
from pathlib import Path

from .. import log
from ..models.guide import Guide
from ..models.ig_info import IgInfo
from ..models.ig_list import IgList
from .helper import read
from .helper import render as render_helper
from .helper import write

FILE_NAME = "ig_list.json"
RENDER_FILE_NAME = "index.html"

TOPIC_REGEX = re.compile(r"^(.+)\s[\-\d\.(ballot|b)]+$")


def update(ig_registry_dir: Path, info: IgInfo) -> IgList:
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
        guide = Guide.model_validate(
            {
                "editions": [info.edition],
                **info.model_dump(),
            }
        )
        ig_list.guides.append(guide)

    write(ig_registry_dir, FILE_NAME, ig_list)
    log.succ(f"updated ig list {ig_registry_dir/FILE_NAME}")

    return ig_list


def render(registry_dir: Path, ig_list: IgList):
    data = {"title": "IG List", "topics": {}}
    for guide in ig_list.guides:
        for edition in guide.editions:
            topic = (
                match[1]
                if (match := TOPIC_REGEX.match(edition.name)) is not None
                else edition.name
            )
            if topic not in data["topics"]:
                data["topics"][topic] = {}

            if edition.name not in data["topics"][topic]:
                data["topics"][topic][edition.name] = []

            g = {
                "name": guide.name,
                "ig_version": edition.ig_version,
                "fhir_version": edition.fhir_version,
                "description": edition.description,
                "url": edition.url,
            }

            data["topics"][topic][edition.name].append(g)

    render_helper(registry_dir, RENDER_FILE_NAME, data, "ig_list.jinja")
    log.succ("rendered ig list")
