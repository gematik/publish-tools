from pydantic import AliasChoices, BaseModel, Field


class IgDef(BaseModel):
    name: str
    category: str
    npm_name: str = Field(
        serialization_alias="npm-name",
        validation_alias=AliasChoices("npm-name", "npm_name"),
    )
    description: str
    canonical: str
    ci_build: str = Field(
        serialization_alias="ci-build",
        validation_alias=AliasChoices("ci-build", "ci_build"),
    )


class Edition(BaseModel):
    name: str
    ig_version: str = Field(
        serialization_alias="ig-version",
        validation_alias=AliasChoices("ig-version", "ig_version"),
    )
    package: str
    fhir_version: list[str] = Field(
        serialization_alias="fhir-version",
        validation_alias=AliasChoices("fhir_version", "fhir-version"),
    )
    url: str
    description: str


class IgInfo(IgDef):
    edition: Edition


class Guide(IgDef):
    editions: list[Edition]


class IgList(BaseModel):
    guides: list[Guide] = []
