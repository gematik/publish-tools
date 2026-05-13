from datetime import date as datetime_date

from pydantic import AliasChoices, AnyUrl, BaseModel, Field

from .guide import Edition
from .sushi_config import SushiConfigReleaseLabel


class IgInfo(BaseModel):
    title: str
    package_id: str = Field(
        serialization_alias="packageId",
        validation_alias=AliasChoices("packageId", "package_id"),
    )
    canonical: AnyUrl
    sequence: str
    version: str
    fhir_version: list[str] = Field(
        serialization_alias="fhir-version",
        validation_alias=AliasChoices("fhir_version", "fhir-version"),
    )
    path: AnyUrl
    desc: str
    date: datetime_date
    release_label: SushiConfigReleaseLabel = Field(
        serialization_alias="releaseLabel",
        validation_alias=AliasChoices("releaseLabel", "release_label"),
    )

    @property
    def package(self):
        return f"{self.package_id}#{self.version}"

    publisher: str

    @property
    def edition(self):
        return Edition(
            name=self.sequence,
            ig_version=self.version,
            package=self.package,
            fhir_version=self.fhir_version,
            url=self.path,
            description=self.desc,
        )


class IgInfoFirst(IgInfo):
    category: str
    introduction: str
    ci_build: AnyUrl = Field(
        serialization_alias="ci-build",
        validation_alias=AliasChoices("ci-build", "ci_build"),
    )
