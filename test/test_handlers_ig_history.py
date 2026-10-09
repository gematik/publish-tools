from pathlib import Path
from tempfile import TemporaryDirectory

from publish_tools.handlers import ig_history
from publish_tools.models.package_list import PackageList


def test_history_selects_latest_stable_release_and_keeps_ci_separate(version_links):
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
    links = version_links(html).links
    assert links["https://example.org/1.9.0"] is False
    assert links["https://example.org/1.10.0"] is False
    assert links["https://example.org/ci"] is False
    assert '<time datetime="2026-01-01">01.01.2026</time>' in html
    assert "Aktuelle Versionen" in html
    assert 'class="publication-table"' in html
    assert html.count('href="https://example.org/1.10.0"') == 4
    assert "Release ·" not in html


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


def test_empty_history_render():
    with TemporaryDirectory() as directory:
        path = Path(directory)
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
