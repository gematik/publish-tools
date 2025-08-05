from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from .models import Guide, IgList


def render_history(file: Path):
    content = file.read_text(encoding="utf-8")
    history = Guide.model_validate_json(content)

    data = history.model_dump()

    # Create sequences
    data["sequences"] = {}
    # Handle sequences
    for edition in sorted(history.editions, key=lambda x: x.ig_version, reverse=True):
        if edition.name not in data["sequences"]:
            data["sequences"][edition.name] = []
        data["sequences"][edition.name].append(edition)

    content = _render(data, "history.jinja")

    output = file.with_name("index.html")
    output.write_text(content, encoding="utf-8")


def render_ig_list(file: Path):
    content = file.read_text(encoding="utf-8")
    ig_list = IgList.model_validate_json(content)

    data = ig_list.model_dump()
    data["title"] = "IG List"
    content = _render(data)

    output = file.with_name("index.html")
    output.write_text(content, encoding="utf-8")


def _render(data: dict, template_name: str) -> str:
    env = Environment(
        loader=PackageLoader("publish_tools"), autoescape=select_autoescape()
    )

    template = env.get_template(template_name)
    return template.render(**data)
