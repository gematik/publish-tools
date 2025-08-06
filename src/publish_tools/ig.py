import json
import shutil
from pathlib import Path

from .ig_history import update_ig_history_file
from .ig_list import update_ig_list
from .models import Edition, IgInfo
from .render import render_history


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


def publish(project_dir: Path, ig_list_file: Path):
    info = get_package_information(project_dir)
    update_ig_list(info, ig_list_file)

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

    archive = Path(
        shutil.make_archive(
            info.edition.package,
            "zip",
            pub_ig_dir,
            pub_ig_version_dir,
        )
    )

    shutil.move(archive, archive_dir / archive.name)

    # Update history file
    hilstory_file = update_ig_history_file(pub_ig_dir, info)
    render_history(hilstory_file)
