from publish_tools.handlers.helper import version_key


def test_numeric_and_prerelease_order():
    versions = ["1.9.0", "1.10.0-rc.2", "1.10.0", "1.10.0-rc.10"]
    assert sorted(versions, key=version_key) == [
        "1.9.0",
        "1.10.0-rc.2",
        "1.10.0-rc.10",
        "1.10.0",
    ]


def test_preview_detection_from_sequence_and_version():
    from publish_tools.handlers.helper import release_channel
    from publish_tools.models.release_channel import ReleaseChannel

    assert release_channel("1.0.0", "Example Ballot") is ReleaseChannel.BALLOT
    assert release_channel("1.0.0", "Example RC 2") is ReleaseChannel.RELEASE_CANDIDATE
    assert release_channel("1.0.0-b1") is ReleaseChannel.BALLOT
    assert release_channel("1.0.0-RC1") is ReleaseChannel.RELEASE_CANDIDATE
    assert release_channel("1.0.0", "Beschreibung") is ReleaseChannel.STABLE
    assert (
        release_channel("1.4.0-rc.1", "TI Common Ballot", "ballot")
        is ReleaseChannel.RELEASE_CANDIDATE
    )
    assert (
        release_channel("1.4.0-ballot.1", "TI Common RC", "release")
        is ReleaseChannel.BALLOT
    )
    assert release_channel("1.4.0-b1", "TI Common RC") is ReleaseChannel.BALLOT
