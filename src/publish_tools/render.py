from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from .models import Guide


def render_history(file: Path):
    content = file.read_text(encoding="utf-8")
    history = Guide.model_validate_json(content)

    env = Environment(
        loader=PackageLoader("publish_tools"), autoescape=select_autoescape()
    )

    data = history.model_dump()

    data["sequences"] = {}
    # Handle sequences
    for edition in sorted(history.editions, key=lambda x: x.ig_version, reverse=True):
        if edition.name not in data["sequences"]:
            data["sequences"][edition.name] = []
        data["sequences"][edition.name].append(edition)

    basic_body = env.get_template("basic_body.jinja")

    output = Path("index.html")
    output.write_text(basic_body.render(**data), encoding="utf-8")
