import re

from jinja2 import Environment, PackageLoader
from jinja2.filters import do_mark_safe as safe
from markupsafe import escape

# Matches 'ballot' or 'Vorabveröffentlichung'
# (with leading separators/spaces) anywhere
REMOVE_TOKEN_REGEX = re.compile(
    r"([\s\-_()/]*)\b(?:ballot|vorabveröffentlichung)\b", re.IGNORECASE
)


def render(data: dict, template_name: str) -> str:
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
