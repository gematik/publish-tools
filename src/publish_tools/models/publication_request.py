from pydantic import AliasChoices, AnyUrl, BaseModel, Field


class PublicationRequest(BaseModel):
    title: str | None = None
    category: str | None = None
    package_id: str = Field(
        serialization_alias="package-id",
        validation_alias=AliasChoices("package-id", "package_id"),
    )
    introduction: str | None = None
    ci_build: AnyUrl | None = Field(
        serialization_alias="ci-build",
        validation_alias=AliasChoices("ci-build", "ci_build"),
        default=None,
    )
    sequence: str
    version: str
    path: AnyUrl
    desc: str
