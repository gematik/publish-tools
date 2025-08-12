import re
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from .ig_list import FILE_NAME as IG_LIST_FILE_NAME
from .models import Guide, IgList

TOPIC_REGEX = re.compile(r"^(.+)\s[\-\d\.(ballot|b)]+$")


def render_history(file: Path):
    content = file.read_text(encoding="utf-8")
    history = Guide.model_validate_json(content)

    data = history.model_dump()

    # Create sequences
    data["sequences"] = {}
    # Handle sequences
    for edition in history.editions:
        if edition.name not in data["sequences"]:
            data["sequences"][edition.name] = []
        data["sequences"][edition.name].append(edition)

    content = _render(data, "history.jinja")

    output = file.with_name("index.html")
    output.write_text(content, encoding="utf-8")


def render_ig_list(registry_dir: Path):
    file = registry_dir / IG_LIST_FILE_NAME
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

    content = _render(data, "ig_list.jinja")

    output = file.with_name("index.html")
    output.write_text(content, encoding="utf-8")


def _render(data: dict, template_name: str) -> str:
    env = Environment(
        loader=PackageLoader("publish_tools"), autoescape=select_autoescape()
    )

    template = env.get_template(template_name)
    return template.render(**data)
