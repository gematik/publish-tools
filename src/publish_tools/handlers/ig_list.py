import re
from pathlib import Path

from .. import log
from ..models.guide import Guide
from ..models.ig_info import IgInfo
from ..models.ig_list import IgList
from .helper import render as render_helper

FILE_NAME = "ig_list.json"
TOPIC_REGEX = re.compile(r"^(.+)\s[\-\d\.(ballot|b)]+$")


def update(info: IgInfo, ig_registry_dir: Path):
    """
    Update the IG List file
    """
    ig_list = None

    ig_list_file = ig_registry_dir / FILE_NAME
    if ig_list_file.exists():
        # Read the existing data
        content = ig_list_file.read_text(encoding="utf-8")
        ig_list = IgList.model_validate_json(content)

    else:
        # Ensure the parent directory exists
        ig_list_file.parent.mkdir(parents=True, exist_ok=True)
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

    content = ig_list.model_dump_json(indent=4, by_alias=True)
    ig_list_file.write_text(content, encoding="utf-8")
    log.succ(f"updated ig list {ig_list_file}")


def render(registry_dir: Path):
    file = registry_dir / FILE_NAME
    content = file.read_text(encoding="utf-8")
    ig_list = IgList.model_validate_json(content)

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

    content = render_helper(data, "ig_list.jinja")

    output = file.with_name("index.html")
    output.write_text(content, encoding="utf-8")
    log.succ("rendered ig list")
