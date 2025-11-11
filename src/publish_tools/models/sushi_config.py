from enum import StrEnum

from pydantic import AliasChoices, AnyUrl, BaseModel, Field


class SushiConfigReleaseLabel(StrEnum):
    CI_BUILD = "ci-build"
    DRAFT = "draft"
    QA_PREVIEW = "qa-preview"
    BALLOT = "ballot"
    TRIAL_USE = "trial-use"
    RELEASE = "release"
    UPDATE = "update"
    NORMATIVE_TRIAL_USE = "normative+trial-use"


class SushiConfig(BaseModel):
    canonical: AnyUrl
    release_label: SushiConfigReleaseLabel = Field(
        serialization_alias="releaseLabel",
        validation_alias=AliasChoices("releaseLabel", "release_label"),
    )
