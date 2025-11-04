from datetime import date as datetime_date
from typing import List

from pydantic import AliasChoices, AnyUrl, BaseModel, Field


class PackageListSimpleEntry(BaseModel):
    version: str
    desc: str
    path: AnyUrl
    status: str
    current: bool


class PackageListCurrentEntry(PackageListSimpleEntry):
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
    list: List[PackageListCurrentEntry | PackageListSpecificEntry] = []
