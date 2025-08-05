from pydantic import BaseModel, Field


class IgDef(BaseModel):
    name: str
    category: str
    npm_name: str = Field(serialization_alias="npm-name")
    description: str
    canonical: str
    ci_build: str = Field(serialization_alias="ci-build")


class Edition(BaseModel):
    name: str
    ig_version: str = Field(serialization_alias="ig-version")
    package: str
    fhir_version: list[str] = Field(serialization_alias="fhir-version")
    url: str
    description: str


class IgInfo(IgDef):
    edition: Edition


class Guide(IgDef):
    editions: list[Edition]


class IgList(BaseModel):
    guides: list[Guide] = []
