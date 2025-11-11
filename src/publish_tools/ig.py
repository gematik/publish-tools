import json
import shutil
from pathlib import Path

import yaml

from . import log
from .handlers import helper, ig_history, ig_list, package_feed, package_list
from .models.guide import Guide
from .models.ig_info import IgInfo
from .models.implementation_guide import ImplementationGuide
from .models.publication_request import PublicationRequest
from .models.sushi_config import SushiConfig

PUB_REQ_FILE = "publication-request.json"
IMP_GUIDE_GLOB = "ImplementationGuide*.json"
SUSHI_CONFIG_FILE = "sushi-config.yaml"


def get_package_information(project_dir: Path) -> IgInfo:
    output_dir = project_dir / "output"

    log.info(f"Get package information from {project_dir}")
    if not (
        imp_guide_file := (
            res[0] if (res := list(output_dir.glob(IMP_GUIDE_GLOB))) else None
        )
    ):
        log.error("Package not built")
        raise Exception("Package not built")

    if not (pub_req_file := project_dir / PUB_REQ_FILE):
        log.error("Publication request missing")
        raise Exception("Publication request missing")

    if not (sushi_config_file := project_dir / SUSHI_CONFIG_FILE):
        log.error("Sushi config missing")
        raise Exception("Sushi config missing")

    imp_guide_cont = json.loads(imp_guide_file.read_text("utf-8"))
    pub_req_cont = json.loads(pub_req_file.read_text("utf-8"))
    sushi_config_cont = yaml.safe_load(sushi_config_file.read_text("utf-8"))

    imp_guide = ImplementationGuide.model_validate(imp_guide_cont)
    pub_req = PublicationRequest.model_validate(pub_req_cont)
    sushi_config = SushiConfig.model_validate(sushi_config_cont)

    info = IgInfo(
        title=pub_req.title,
        category=pub_req.category,
        publisher=imp_guide.publisher,
        package_id=imp_guide.package_id,
        introduction=pub_req.introduction,
        canonical=sushi_config.canonical,
        ci_build=pub_req.ci_build,
        sequence=pub_req.sequence,
        version=pub_req.version,
        fhir_version=imp_guide.fhir_version,
        path=pub_req.path,
        desc=pub_req.desc,
        date=imp_guide.date,
        release_label=sushi_config.release_label,
    )

    return info


def publish(project_dir: Path, ig_registry_dir: Path):
    info = get_package_information(project_dir)
    log.info(f"publishing {info.title} ({info.package})")

    ######
    # Create directory for IG contents
    ######
    project_dir = project_dir.absolute()
    pub_dir = project_dir / "publish"
    pub_dir.mkdir(parents=True, exist_ok=True)

    pub_project = info.canonical.path.rsplit("/", 1)[-1]
    pub_ig_dir = pub_dir / pub_project

    # If project subdir exists, migrate data
    if pub_ig_dir.exists():
        for file in pub_ig_dir.iterdir():
            if file.suffix in [".json", ".html"]:
                shutil.move(file, pub_dir)
        pub_ig_dir.rmdir()

    del pub_ig_dir

    # Migrate history file to package list
    if history := helper.read(pub_dir, ig_history.FILE_NAME, Guide):
        plist = package_list.from_history(history)
        helper.write(pub_dir, package_list.FILE_NAME, plist)

        # Remove history file after migration
        (pub_dir / ig_history.FILE_NAME).unlink()

    plist = package_list.update(pub_dir, info)
    ig_history.render(pub_dir, plist)

    # Update ig list
    i_list = ig_list.update(ig_registry_dir, info)
    ig_list.render(ig_registry_dir, i_list)
    package_feed.update(ig_registry_dir, info)
