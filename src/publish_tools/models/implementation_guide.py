from datetime import date as datetime_date
from enum import StrEnum

from pydantic import AliasChoices, AnyUrl, BaseModel, Field


class ImplementationGuideStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"
    UNKNOWN = "unknown"


class ImplementationGuideDefinitionExtensionExtenion(BaseModel):
    url: str
    valueString: str | None = None
    valueCode: str | None = None


class ImplementationGuideDefinitionExtension(BaseModel):
    extension: list[ImplementationGuideDefinitionExtensionExtenion] = []


class ImplementationGuideDefinition(BaseModel):
    extension: list[ImplementationGuideDefinitionExtension] = []


class ImplementationGuide(BaseModel):
    id: str
    url: AnyUrl
    version: str
    name: str
    title: str
    status: ImplementationGuideStatus
    experimental: bool
    date: datetime_date
    publisher: str
    copyright: str | None = None
    package_id: str = Field(
        serialization_alias="packageId",
        validation_alias=AliasChoices("packageId", "package_id"),
    )
    license: str
    fhir_version: list[str] = Field(
        serialization_alias="fhirVersion",
        validation_alias=AliasChoices("fhirVersion", "fhir_version"),
    )
    definition: ImplementationGuideDefinition = ImplementationGuideDefinition()

    @property
    def parameters(self):
        params = {}
        for ext in self.definition.extension:
            code = None
            value = None
            for extext in ext.extension:
                if extext.url == "code":
                    code = extext.valueCode or extext.valueString

                elif extext.url == "value":
                    value = extext.valueCode or extext.valueString

            if code is not None and value is not None:
                params[code] = value

        return params
