from enum import StrEnum


class ReleaseChannel(StrEnum):
    STABLE = "Veröffentlichungen"
    RELEASE_CANDIDATE = "Release Candidate"
    BALLOT = "Ballot"
