from pydantic import AliasChoices, AnyUrl, BaseModel, Field


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
    url: AnyUrl
    description: str


class Guide(BaseModel):
    name: str
    category: str
    npm_name: str = Field(
        serialization_alias="npm-name",
        validation_alias=AliasChoices("npm-name", "npm_name"),
    )
    description: str
    canonical: AnyUrl
    ci_build: AnyUrl = Field(
        serialization_alias="ci-build",
        validation_alias=AliasChoices("ci-build", "ci_build"),
    )
    editions: list[Edition]
