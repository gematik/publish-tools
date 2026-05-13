from pydantic import AliasChoices, AnyUrl, BaseModel, Field


class PublicationRequest(BaseModel):
    title: str | None = None
    package_id: str = Field(
        serialization_alias="package-id",
        validation_alias=AliasChoices("package-id", "package_id"),
    )
    sequence: str
    version: str
    path: AnyUrl
    desc: str


class PublicationRequestFirst(PublicationRequest):
    ci_build: AnyUrl = Field(
        serialization_alias="ci-build",
        validation_alias=AliasChoices("ci-build", "ci_build"),
    )
    registry_description: str = Field(
        serialization_alias="registry-description",
        validation_alias=AliasChoices("registry-description", "registry_description"),
    )
    registry_country: str = Field(
        serialization_alias="registry-country",
        validation_alias=AliasChoices("registry-country", "registry_country"),
    )
    registry_authority: str = Field(
        serialization_alias="registry-authority",
        validation_alias=AliasChoices("registry-authority", "registry_authority"),
    )
    category: str
    introduction: str
