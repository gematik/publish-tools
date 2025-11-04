from datetime import date as datetime_date
from typing import List

from pydantic import AliasChoices, AnyUrl, BaseModel, Field

from .sushi_config import SushiConfigReleaseLabel


class PackageListSimpleEntry(BaseModel):
    version: str
    desc: str
    path: AnyUrl
    status: SushiConfigReleaseLabel
    current: bool


class PackageListCiBuildEntry(PackageListSimpleEntry):
    version: str = "current"
    status: SushiConfigReleaseLabel = SushiConfigReleaseLabel.CI_BUILD
    current: bool = True


class PackageListSpecificEntry(PackageListSimpleEntry):
    date: datetime_date
    sequence: str
    fhir_version: str = Field(
        serialization_alias="fhirversion",
        validation_alias=AliasChoices("fhirversion", "fhir_version"),
    )
    current: bool = False


class PackageList(BaseModel):
    package_id: str = Field(
        serialization_alias="package-id",
        validation_alias=AliasChoices("package_id", "package-id"),
    )
    canonical: AnyUrl
    title: str
    introduction: str
    list: List[PackageListCiBuildEntry | PackageListSpecificEntry] = []
