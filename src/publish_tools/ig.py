import json
import shutil
from pathlib import Path

from pydantic import ValidationError

import yaml

from . import log
from .handlers import helper, ig_history, ig_list, package_feed, package_list
from .models.guide import Guide
from .models.ig_info import IgInfo, IgInfoFirst
from .models.implementation_guide import ImplementationGuide
from .models.publication_request import PublicationRequest, PublicationRequestFirst
from .models.sushi_config import SushiConfig

PUB_REQ_FILE = "publication-request.json"
IMP_GUIDE_GLOB = "ImplementationGuide*.json"
SUSHI_CONFIG_FILE = "sushi-config.yaml"


def get_package_information(project_dir: Path) -> IgInfo | IgInfoFirst:
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

    try:
        imp_guide = ImplementationGuide.model_validate(imp_guide_cont)

    except ValidationError as e:
        raise Exception("Invalid Implementation Guide: {}", e)

    try:
        sushi_config = SushiConfig.model_validate(sushi_config_cont)

    except ValidationError as e:
        raise Exception("Invalid Sushi Config: {}", e)

    if pub_req_cont.get("first"):
        try:
            pub_req = PublicationRequestFirst.model_validate(pub_req_cont)

        except ValidationError as e:
            raise Exception("Invalid Publication Request: {}".format(e))

        info = IgInfoFirst(
            title=imp_guide.title,
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

    else:
        try:
            pub_req = PublicationRequest.model_validate(pub_req_cont)

        except ValidationError as e:
            raise Exception("Invalid Publication Request: {}", e)

        info = IgInfo(
            title=imp_guide.title,
            publisher=imp_guide.publisher,
            package_id=imp_guide.package_id,
            canonical=sushi_config.canonical,
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
        log.info("migrating from old structure")
        for file in pub_ig_dir.iterdir():
            if file.suffix in [".json", ".html"]:
                log.info("migrating {}".format(file))
                shutil.move(file, pub_dir)
            else:
                file.unlink()
        pub_ig_dir.rmdir()
        log.succ("finished migration")

    del pub_ig_dir

    # Migrate history file to package list
    if history := helper.read(pub_dir, ig_history.FILE_NAME, Guide):
        log.info("migrating from `ig_history.json` to `package_list.json`")
        plist = package_list.from_history(history)
        helper.write(pub_dir, package_list.FILE_NAME, plist)

        # Remove history file after migration
        (pub_dir / ig_history.FILE_NAME).unlink()
        log.succ("finished migration")

    plist = package_list.update(pub_dir, info)
    ig_history.render(pub_dir, plist)

    # Update ig list
    i_list = ig_list.update(ig_registry_dir, info)
    ig_list.render(ig_registry_dir, i_list)
    package_feed.update(ig_registry_dir, info)
