from pathlib import Path

from .models import Guide, IgInfo


def update_ig_history_file(ig_dir: Path, info: IgInfo) -> Path:
    ig_dir.mkdir(parents=True, exist_ok=True)

    ig_history_file = ig_dir / "ig_history.json"
    if ig_history_file.exists():
        content = ig_history_file.read_text(encoding="utf-8")
        guide = Guide.model_validate_json(content)

        edition_found = False
        for i, edition in enumerate(guide.editions):
            if edition.package == info.edition.package:
                guide.editions[i] = info.edition
                edition_found = True
                break

        if not edition_found:
            guide.editions.append(info.edition)

    else:
        guide = Guide.model_validate(
            {
                "editions": [info.edition],
                **info.model_dump(),
            }
        )

    content = guide.model_dump_json(indent=4, by_alias=True)
    ig_history_file.write_text(content, encoding="utf-8")

    return ig_history_file
