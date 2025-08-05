import json
from pathlib import Path

from .models import Edition, Guide, IgInfo, IgList


def get_package_information(project_dir: Path) -> IgInfo:
    output_dir = project_dir / "output"

    ig_file = (
        res[0]
        if len(res := list(output_dir.glob("ImplementationGuide*.json"))) == 1
        else None
    )
    if ig_file is None:
        raise Exception("package not built")

    pub_file = project_dir / "publication-request.json"
    if pub_file is None:
        raise Exception("publication request missing")

    ig_info = json.loads(ig_file.read_text(encoding="utf-8"))
    pub_info = json.loads(pub_file.read_text(encoding="utf-8"))

    info = IgInfo(
        name=pub_info["title"],
        category=pub_info["category"],
        npm_name=pub_info["package-id"],
        description=pub_info["introduction"],
        canonical=ig_info["url"].rsplit("/", 2)[0],
        ci_build=pub_info["ci-build"],
        edition=Edition(
            name=pub_info["sequence"],
            ig_version=pub_info["version"],
            package=f"{pub_info["package-id"]}#{pub_info["version"]}",
            fhir_version=ig_info["fhirVersion"],
            url=pub_info["path"],
            description=pub_info["desc"],
        ),
    )

    return info


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

    content = ig_list.model_dump_json(indent=4)
    ig_list_file.write_text(content, encoding="utf-8")


def publish(project_dir: Path, info: IgInfo):
    ######
    # Create directory for IG contents
    ######
    pub_dir = project_dir / "publish"
    pub_dir.mkdir(parents=True, exist_ok=True)

    output_dir = project_dir / "output"

    pub_project = info.canonical.rsplit("/", 1)[1]
    pub_ig_dir = pub_dir / pub_project
    pub_ig_version_dir = pub_ig_dir / info.edition.ig_version

    # Clear previous content
    if pub_ig_dir.exists():
        shutil.rmtree(pub_ig_version_dir)

    shutil.copytree(output_dir, pub_ig_version_dir)

    ######
    # Create archive
    ######
    archive_dir = pub_dir / "ig-build-zips"
    archive_dir.mkdir(parents=True, exist_ok=True)

    archive = shutil.make_archive(
        info.edition.package, "zip", pub_ig_dir, pub_ig_version_dir
    )

    shutil.move(archive, archive_dir)
