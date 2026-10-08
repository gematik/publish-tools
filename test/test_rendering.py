from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory

from publish_tools.handlers import ig_history, ig_list
from publish_tools.handlers.helper import version_key
from publish_tools.models.ig_list import IgList
from publish_tools.models.package_list import PackageList


class VersionLinks(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.depth = 0
        self.links = {}
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "details":
            assert "open" not in dict(attrs)
            self.depth += 1
        if tag == "a":
            self.links[dict(attrs)["href"]] = self.depth > 0

    def handle_endtag(self, tag):
        if tag == "details":
            self.depth -= 1


def test_numeric_and_prerelease_order():
    versions = ["1.9.0", "1.10.0-rc.2", "1.10.0", "1.10.0-rc.10"]
    assert sorted(versions, key=version_key) == [
        "1.9.0",
        "1.10.0-rc.2",
        "1.10.0-rc.10",
        "1.10.0",
    ]


def test_list_groups_versions_by_package():
    guides = []
    for package in ["one", "two"]:
        guides.append(
            dict(
                name="Same title",
                npm_name=package,
                category="test",
                canonical="https://example.org/",
                ci_build="https://example.org/ci",
                description="Guide",
                editions=[
                    dict(
                        name="Release",
                        ig_version=version,
                        package=f"{package}#{version}",
                        fhir_version=["4.0.1"],
                        url=f"https://example.org/{package}/{version}",
                        description="<script>unsafe</script>",
                    )
                    for version in ["1.9.0", "1.10.0"]
                ],
            )
        )
    with TemporaryDirectory() as directory:
        ig_list.render(Path(directory), IgList(guides=guides))
        html = (Path(directory) / "index.html").read_text()
    links = VersionLinks(html).links
    for package in ["one", "two"]:
        assert links[f"https://example.org/{package}/1.10.0"] is False
        assert links[f"https://example.org/{package}/1.9.0"] is True
    assert "<script>unsafe</script>" not in html
    assert 'href="https://example.org/one/1.10.0">1.10.0</a>' in html
    assert '<a class="ig-name"' not in html


def test_history_selects_latest_stable_release_and_keeps_ci_separate():
    plist = PackageList.model_validate(
        dict(
            package_id="example",
            canonical="https://example.org/",
            title="Example",
            introduction="Test",
            list=[
                dict(path="https://example.org/ci", desc="CI"),
                *[
                    dict(
                        version=version,
                        path=f"https://example.org/{version}",
                        desc="Release",
                        status="release",
                        current=current,
                        date="2026-01-01",
                        sequence="Release",
                        fhir_version="4.0.1",
                    )
                    for version, current in [("1.9.0", True), ("1.10.0", False)]
                ],
            ],
        )
    )
    with TemporaryDirectory() as directory:
        ig_history.render(Path(directory), plist)
        html = (Path(directory) / "index.html").read_text()
    links = VersionLinks(html).links
    assert links["https://example.org/1.9.0"] is False
    assert links["https://example.org/1.10.0"] is False
    assert links["https://example.org/ci"] is False
    assert '<time datetime="2026-01-01">01.01.2026</time>' in html
    assert "Aktuelle Versionen" in html
    assert 'class="publication-table"' in html
    assert html.count('href="https://example.org/1.10.0"') == 4
    assert "Release ·" not in html


def test_empty_list_and_history_render():
    with TemporaryDirectory() as directory:
        path = Path(directory)
        ig_list.render(path, IgList())
        assert "Noch keine Pakete" in (path / "index.html").read_text()
        ig_history.render(
            path,
            PackageList(
                package_id="example",
                canonical="https://example.org/",
                title="Example",
                introduction="Test",
            ),
        )
        assert "Noch keine Version" in (path / "index.html").read_text()


def test_package_groups_combine_sequences_and_keep_previews_separate():
    editions = []
    for sequence, versions in [
        (
            "Sequence A",
            [
                "1.9.0",
                "1.10.0",
                "2.0.0-ballot.1",
                "2.0.0-ballot.2",
                "2.0.0-rc.1",
                "2.0.0-rc.2",
            ],
        ),
        ("Sequence B", ["3.0.0"]),
    ]:
        for version in versions:
            editions.append(
                dict(
                    name=sequence,
                    ig_version=version,
                    package=f"example#{version}",
                    fhir_version=["4.0.1"],
                    url=f"https://example.org/{version}",
                    description=sequence,
                )
            )
    guide = dict(
        name="Example",
        npm_name="example",
        category="test",
        canonical="https://example.org/",
        ci_build="https://example.org/ci",
        description="Guide",
        editions=editions,
    )
    with TemporaryDirectory() as directory:
        ig_list.render(Path(directory), IgList(guides=[guide]))
        html = (Path(directory) / "index.html").read_text()
    links = VersionLinks(html).links
    for version in ["2.0.0-ballot.2", "2.0.0-rc.2", "3.0.0"]:
        assert links[f"https://example.org/{version}"] is False
    for version in ["1.9.0", "1.10.0", "2.0.0-ballot.1", "2.0.0-rc.1"]:
        assert links[f"https://example.org/{version}"] is True
    assert "Sequence A" in html and "Sequence B" in html
    assert "Ballot" in html and "Release Candidate" in html


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


def test_legacy_dates_are_ignored_and_older_ballots_collapse():
    versions = [
        ("2.0.0", "2026-06-01", "release"),
        ("3.0.0-ballot.1", "2026-05-01", "ballot"),
        ("3.0.0-ballot.2", "2026-07-01", "ballot"),
        ("3.0.0-ballot.3", "2026-08-01", "ballot"),
    ]
    guide = dict(
        name="Example",
        npm_name="example",
        category="test",
        canonical="https://example.org/",
        ci_build="https://example.org/ci",
        description="Guide",
        editions=[
            dict(
                name="Sequence",
                ig_version=v,
                package=f"example#{v}",
                fhir_version=["4.0.1"],
                date=d,
                status=status,
                url=f"https://example.org/{v}",
                description="Release",
            )
            for v, d, status in versions
        ],
    )
    with TemporaryDirectory() as directory:
        ig_list.render(Path(directory), IgList(guides=[guide]))
        html = (Path(directory) / "index.html").read_text()
    links = VersionLinks(html).links
    assert links["https://example.org/2.0.0"] is False
    assert links["https://example.org/3.0.0-ballot.1"] is True
    assert links["https://example.org/3.0.0-ballot.2"] is True
    assert links["https://example.org/3.0.0-ballot.3"] is False
    assert html.count('class="package-id"') == 1
    assert 'alt="gematik"' in html
    assert "Veröffentlicht:" not in html
    assert "2026-06-01" not in html
    edition = IgList(guides=[guide]).guides[0].editions[0]
    assert "date" not in edition.model_dump()
    assert "status" not in edition.model_dump()
    assert "Sequence: Sequence" in html


def test_from_history_includes_current_build():
    from publish_tools.handlers.package_list import from_history
    from publish_tools.models.guide import Guide

    guide = Guide(
        name="Example",
        npm_name="example",
        category="test",
        canonical="https://example.org/",
        ci_build="https://example.org/build",
        description="Guide",
        editions=[],
    )
    plist = from_history(guide)
    assert len(plist.list) == 1
    assert plist.list[0].version == "current"
    assert plist.list[0].current is True
    with TemporaryDirectory() as directory:
        ig_history.render(Path(directory), plist)
        html = (Path(directory) / "index.html").read_text()
    assert "Current" in html
    assert "https://example.org/build" in html
    assert VersionLinks(html).links["https://example.org/build"] is False


def test_package_families_keep_each_package_visible():
    ids = [
        "de.gematik.epa",
        "de.gematik.epa.medication",
        "de.gematik.epa.medication.examples",
        "de.gematik.tiflow.core",
        "de.gematik.tiflow.test",
        "de.gematik.epaother",
    ]
    families = ig_list.package_families(ids)
    assert all(families[package] == "de.gematik.epa" for package in ids[:3])
    assert all(families[package] == "de.gematik.tiflow" for package in ids[3:5])
    assert families[ids[-1]] == ids[-1]


def test_package_families_support_long_ids_and_single_packages():
    ids = [
        "de.gematik.ig.sandbox",
        "de.gematik.other.deep.core",
        "de.gematik.other.deep.examples",
        "org.example.parent",
        "org.example.parent.child",
    ]
    families = ig_list.package_families(ids)
    assert families[ids[0]] == ids[0]
    assert families[ids[1]] == "de.gematik.other.deep"
    assert families[ids[2]] == "de.gematik.other.deep"
    assert families[ids[4]] == ids[3]
    assert ig_list.package_families([]) == {}


def test_multiple_igs_per_package_version_are_preserved():
    from unittest.mock import patch
    from publish_tools.models.guide import Guide
    from publish_tools.models.ig_info import IgInfo

    editions = [
        dict(
            name=f"ISiK {module} {version}",
            ig_version=version,
            package=f"de.gematik.isik#{version}",
            fhir_version=["4.0.1"],
            url=f"https://example.org/{module}/{version}",
            description=f"{module} guide",
        )
        for version in ["5.0.0", "6.0.0", "7.0.0-rc.1", "7.0.0-rc.2"]
        for module in ["Basis", "Labor"]
    ]
    guide = Guide(
        name="ISiK",
        npm_name="de.gematik.isik",
        category="test",
        canonical="https://example.org/",
        ci_build="https://example.org/ci",
        description="Guide",
        editions=editions,
    )
    registry = IgList(guides=[guide])
    with TemporaryDirectory() as directory:
        path = Path(directory)
        ig_list.render(path, registry)
        html = (path / "index.html").read_text()
        links = VersionLinks(html).links
        for module in ["Basis", "Labor"]:
            assert links[f"https://example.org/{module}/6.0.0"] is False
            assert links[f"https://example.org/{module}/5.0.0"] is True
            assert links[f"https://example.org/{module}/7.0.0-rc.2"] is False
            assert links[f"https://example.org/{module}/7.0.0-rc.1"] is True
        assert html.count(">6.0.0</span>") == 1
        assert (
            '<a class="ig-name" href="https://example.org/Basis/6.0.0">Basis guide</a>'
            in html
        )
        assert (
            '<a class="ig-name" href="https://example.org/Labor/6.0.0">Labor guide</a>'
            in html
        )
        assert "IG 1 öffnen" not in html
        assert html.count("ISiK Basis 6.0.0") == 1
        info = IgInfo(
            title="ISiK",
            package_id="de.gematik.isik",
            canonical="https://example.org/",
            sequence="ISiK Labor 6.0.0",
            version="6.0.0",
            fhir_version=["4.0.1"],
            path="https://example.org/Labor/6.0.0",
            desc="Updated labor",
            date="2026-01-01",
            release_label="release",
            publisher="Test",
        )
        with patch.object(ig_list, "read", return_value=registry):
            result = ig_list.update(path, info)
        assert len(result.guides[0].editions) == 8
        assert result.guides[0].editions[2].description == "Basis guide"
        assert result.guides[0].editions[3].description == "Updated labor"


def test_history_separates_previews_within_same_sequence():
    from unittest.mock import patch

    plist = PackageList.model_validate(
        dict(
            package_id="example",
            canonical="https://example.org/",
            title="Example",
            introduction="Test",
            list=[
                dict(
                    version=version,
                    path=f"https://example.org/{version}",
                    desc="Release",
                    status=status,
                    current=False,
                    date="2026-01-01",
                    sequence="Same sequence",
                    fhir_version="4.0.1",
                )
                for version, status in [
                    ("1.0.0", "release"),
                    ("1.1.0-rc.1", "ballot"),
                    ("1.1.0-ballot.1", "ballot"),
                ]
            ],
        )
    )
    with patch.object(ig_history, "render_helper") as render:
        ig_history.render(Path("."), plist)
    channels = render.call_args.args[2]["channels"]
    assert [channel["name"] for channel in channels] == [
        "Veröffentlichungen",
        "Release Candidate",
        "Ballot",
    ]
    assert [
        channel["sequences"]["Same sequence"][0].version for channel in channels
    ] == ["1.0.0", "1.1.0-rc.1", "1.1.0-ballot.1"]


def test_history_current_excludes_marked_current_previews():
    from unittest.mock import patch

    for preview in ["2.0.0-rc.1", "2.0.0-ballot.1"]:
        plist = PackageList.model_validate(
            dict(
                package_id="example",
                canonical="https://example.org/",
                title="Example",
                introduction="Test",
                list=[
                    dict(path="https://example.org/build", desc="CI"),
                    *[
                        dict(
                            version=version,
                            path=f"https://example.org/{version}",
                            desc="Release",
                            status=status,
                            current=current,
                            date=date,
                            sequence="Test",
                            fhir_version="4.0.1",
                        )
                        for version, status, current, date in [
                            ("1.0.0", "release", False, "2026-01-01"),
                            (preview, "ballot", True, "2026-02-01"),
                        ]
                    ],
                ],
            )
        )
        with patch.object(ig_history, "render_helper") as render:
            ig_history.render(Path("."), plist)
        data = render.call_args.args[2]
        assert [entry.version for entry in data["current_entries"]] == [
            "1.0.0",
            "current",
        ]
        assert data["channels"][1]["current"] == []
        plist.list = [plist.list[0], plist.list[2]]
        with patch.object(ig_history, "render_helper") as render:
            ig_history.render(Path("."), plist)
        assert [
            entry.version for entry in render.call_args.args[2]["current_entries"]
        ] == ["current"]
