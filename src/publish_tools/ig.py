import json
from pathlib import Path

from . import log
from .handlers import ig_history, ig_list, package_feed
from .models.guide import Edition, IgInfo


def get_package_information(project_dir: Path) -> IgInfo:
    output_dir = project_dir / "output"

    log.info(f"get package information from {project_dir}")
    ig_file = (
        res[0]
        if len(res := list(output_dir.glob("ImplementationGuide*.json"))) == 1
        else None
    )
    if ig_file is None:
        log.error("package not built")
        raise Exception("package not built")

    pub_file = project_dir / "publication-request.json"
    if pub_file is None:
        log.error("publication request missing")
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
        ci_build=pub_info.get("ci-build", ""),
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
    log.info(f"publishing {info.name} ({info.edition.package})")

    ######
    # Create directory for IG contents
    ######
    project_dir = project_dir.absolute()
    pub_dir = project_dir / "publish"
    pub_dir.mkdir(parents=True, exist_ok=True)

    pub_project = info.canonical.rsplit("/", 1)[1]
    pub_ig_dir = pub_dir / pub_project

    # Update history file
    history_file = ig_history.update(pub_ig_dir, info)
    ig_history.render(history_file)

    # Update ig list and package feed
    ig_list.update(info, ig_registry_dir)
    ig_list.render(ig_registry_dir)

    package_feed.update(ig_registry_dir, info)
