import json
import shutil
from pathlib import Path

from .ig_history import update_ig_history_file
from .ig_list import update_ig_list
from .log import log_error, log_info, log_succ
from .models import Edition, IgInfo
from .package_feed import update_package_feed
from .render import render_history, render_ig_list


def get_package_information(project_dir: Path) -> IgInfo:
    output_dir = project_dir / "output"

    log_info(f"get package information from {project_dir}")
    ig_file = (
        res[0]
        if len(res := list(output_dir.glob("ImplementationGuide*.json"))) == 1
        else None
    )
    if ig_file is None:
        log_error("package not built")
        raise Exception("package not built")

    pub_file = project_dir / "publication-request.json"
    if pub_file is None:
        log_error("publication request missing")
        raise Exception("publication request missing")

    ig_info = json.loads(ig_file.read_text(encoding="utf-8"))
    pub_info = json.loads(pub_file.read_text(encoding="utf-8"))

    info = IgInfo(
        name=pub_info["title"],
        category=pub_info["category"],
        publisher=ig_info["publisher"],
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


def publish(project_dir: Path, ig_registry_dir: Path):
    info = get_package_information(project_dir)
    log_info(f"publishing {info.name} ({info.edition.package})")

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
        log_info("removed previous versioned IG")

    shutil.copytree(output_dir, pub_ig_version_dir)
    log_succ("created versioned IG")

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
    log_succ("created IG archive")

    # Update history file
    history_file = update_ig_history_file(pub_ig_dir, info)
    render_history(history_file)

    # Update ig list and package feed
    update_ig_list(info, ig_registry_dir)
    render_ig_list(ig_registry_dir)

    update_package_feed(ig_registry_dir, info)
