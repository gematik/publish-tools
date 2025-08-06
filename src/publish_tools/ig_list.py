from pathlib import Path

from .models import Guide, IgInfo, IgList


def update_ig_list(info: IgInfo, ig_list_file: Path):
    ig_list = None

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
        if guide.npm_name == info.npm_name:

            edition_found = False
            for i, edition in enumerate(guide.editions):
                if edition.package == info.edition.package:
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
