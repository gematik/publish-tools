import json
from pathlib import Path

from .models import Edition, Guide


def get_package_information(project_dir: Path) -> Guide:
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

    info = Guide(
        name=pub_info["title"],
        category=pub_info["category"],
        npm_name=pub_info["package-id"],
        description=pub_info["introduction"],
        canonical=ig_info["url"].rsplit("/", 2)[0],
        ci_build=pub_info["ci-build"],
        editions=[
            Edition(
                name=pub_info["sequence"],
                ig_version=pub_info["version"],
                package=f"{pub_info["package-id"]}#{pub_info["version"]}",
                fhir_version=ig_info["fhirVersion"],
                url=pub_info["path"],
                description=pub_info["desc"],
            )
        ],
    )

    return info
