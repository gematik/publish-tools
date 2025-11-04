from pydantic import AliasChoices, AnyUrl, BaseModel, Field


class PublicationRequest(BaseModel):
    title: str
    category: str
    package_id: str = Field(
        serialization_alias="package-id",
        validation_alias=AliasChoices("package-id", "package_id"),
    )
    introduction: str
    ci_build: str = Field(
        serialization_alias="ci-build",
        validation_alias=AliasChoices("ci-build", "ci_build"),
        default="",
    )
    sequence: str
    version: str
    path: AnyUrl
    desc: str
