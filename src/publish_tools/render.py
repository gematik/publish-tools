import re
from pathlib import Path

from jinja2 import Environment, PackageLoader
from jinja2.filters import do_mark_safe as safe
from markupsafe import escape

from .ig_list import FILE_NAME as IG_LIST_FILE_NAME
from .log import log_succ
from .models import Guide, IgList

TOPIC_REGEX = re.compile(r"^(.+)\s[\-\d\.(ballot|b)]+$")

# Matches 'ballot' or 'Vorabveröffentlichung'
# (with leading separators/spaces) anywhere
REMOVE_TOKEN_REGEX = re.compile(
    r"([\s\-_()/]*)\b(?:ballot|vorabveröffentlichung)\b", re.IGNORECASE
)


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
    log_succ("rendered ig history")


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
    log_succ("rendered ig list")


def _render(data: dict, template_name: str) -> str:
    env = Environment(loader=PackageLoader("publish_tools"))
    env.filters["sort_sequences"] = sort_sequences
    env.filters["safe_escape"] = safe_escape

    template = env.get_template(template_name)
    return template.render(**data)


def sort_sequences(items: list[tuple[str, dict]], reverse=False):
    """
    Sort a dictionary with sequence names as keys

    Behaves like the standard sorting except for keys containing the word
    `ballot` or `Vorabveröffentlichung` always being sorted after the ones
    without the token. This stays the same even for `reverse=True`.
    """

    def base_key(key: str) -> str:
        # Remove ballot/Vorabveröffentlichung token from sorting key
        cleaned = REMOVE_TOKEN_REGEX.sub("", key)

        # Make sure the sorting key is lowercase to avoid lowercase and
        # uppercase keys being strangly sorted
        return cleaned.strip().lower()

    # Group the entries by key without the token
    groups: dict[str, list[tuple[str, dict]]] = {}
    for k, v in items:
        groups.setdefault(base_key(k), []).append((k, v))

    result: list[tuple[str, dict]] = []
    for _, values in sorted(
        groups.items(), key=lambda x: x[0].lower(), reverse=reverse
    ):
        result.extend(sorted(values))

    return result


def safe_escape(text: str) -> str:
    """
    Escape special symbols, especifically umlauts.
    """

    # Use the default escaping function, while converting back to string to
    # avoid later escaping again like the '&' from the umlauts
    text = str(escape(text))

    mapping = {
        "ä": "&auml;",
        "ö": "&ouml;",
        "ü": "&uuml;",
        "Ä": "&Auml;",
        "Ö": "&Ouml;",
        "Ü": "&Uuml;",
        "ß": "&szlig;",
    }

    for k, v in mapping.items():
        text = text.replace(k, v)

    # Mark this as safe so it will not be escaped later again
    return safe(text)
