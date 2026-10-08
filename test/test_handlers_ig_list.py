import json
from pathlib import Path
import tempfile
from tempfile import TemporaryDirectory
import unittest

from deepdiff import DeepDiff

from publish_tools.handlers import ig_list, helper
from publish_tools.models.ig_list import IgList
from publish_tools.models.ig_info import IgInfo, IgInfoFirst


class TestUpdate(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        return super().setUp()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        return super().tearDown()

    def setupFile(self, data: dict):
        content = IgList.model_validate(data)

        file = Path(self.tmpdir.name) / ig_list.FILE_NAME
        helper.write(file.parent, file.name, content)

    def process(
        self,
        input_data: dict,
        wanted: dict | None = None,
        setup_data: dict | None = None,
        first: bool = False,
    ):

        if setup_data:
            self.setupFile(setup_data)

        try:
            if first:
                input = IgInfoFirst.model_validate(input_data)

            else:
                input = IgInfo.model_validate(input_data)

            res = ig_list.update(Path(self.tmpdir.name), input)

            if wanted:
                res = json.loads(res.model_dump_json())

                diff = DeepDiff(wanted, res)
                self.maxDiff = None
                self.assertDictEqual(diff, {})

        except Exception as e:
            if wanted:
                self.fail(e)

        else:
            if not wanted:
                self.fail("Expected Exception not raised")

    def test_file_not_exists(self):

        input_data = {
            "title": "Example IG",
            "packageId": "org.example.ig",
            "canonical": "http://example.org/ig",
            "ci-build": "http://example.org/ig/build",
            "sequence": "Test",
            "version": "0.0.1",
            "fhir_version": ["4.0.1"],
            "path": "http://example.org/ig/0.0.1",
            "desc": "Example IG Release 0.0.1",
            "date": "2000-01-01",
            "releaseLabel": "release",
            "publisher": "ExamplePublisher",
            "category": "example",
            "introduction": "Example IG description",
        }

        wanted = {
            "guides": [
                {
                    "name": "Example IG",
                    "category": "example",
                    "npm_name": "org.example.ig",
                    "description": "Example IG description",
                    "canonical": "http://example.org/ig",
                    "ci_build": "http://example.org/ig/build",
                    "editions": [
                        {
                            "name": "Test",
                            "ig_version": "0.0.1",
                            "package": "org.example.ig#0.0.1",
                            "fhir_version": ["4.0.1"],
                            "url": "http://example.org/ig/0.0.1",
                            "description": "Example IG Release 0.0.1",
                        },
                    ],
                }
            ]
        }

        self.process(input_data=input_data, wanted=wanted, first=True)

    def test_guide_not_exists(self):
        setup_data = {"guides": []}

        input_data = {
            "title": "Example IG",
            "packageId": "org.example.ig",
            "canonical": "http://example.org/ig",
            "ci-build": "http://example.org/ig/build",
            "sequence": "Test",
            "version": "0.0.1",
            "fhir_version": ["4.0.1"],
            "path": "http://example.org/ig/0.0.1",
            "desc": "Example IG Release 0.0.1",
            "date": "2000-01-01",
            "releaseLabel": "release",
            "publisher": "ExamplePublisher",
            "category": "example",
            "introduction": "Example IG description",
        }

        wanted = {
            "guides": [
                {
                    "name": "Example IG",
                    "category": "example",
                    "npm_name": "org.example.ig",
                    "description": "Example IG description",
                    "canonical": "http://example.org/ig",
                    "ci_build": "http://example.org/ig/build",
                    "editions": [
                        {
                            "name": "Test",
                            "ig_version": "0.0.1",
                            "package": "org.example.ig#0.0.1",
                            "fhir_version": ["4.0.1"],
                            "url": "http://example.org/ig/0.0.1",
                            "description": "Example IG Release 0.0.1",
                        },
                    ],
                }
            ]
        }

        self.process(
            setup_data=setup_data, input_data=input_data, wanted=wanted, first=True
        )

    def test_guide_not_exists_not_first(self):
        setup_data = {"guides": []}

        input_data = {
            "packageId": "org.example.ig",
            "canonical": "http://example.org/ig",
            "ci-build": "http://example.org/ig/build",
            "sequence": "Test",
            "version": "0.0.1",
            "fhir_version": ["4.0.1"],
            "path": "http://example.org/ig/0.0.1",
            "desc": "Example IG Release 0.0.1",
            "date": "2000-01-01",
            "releaseLabel": "release",
            "publisher": "ExamplePublisher",
        }

        wanted = {
            "guides": [
                {
                    "name": "ExampleIG",
                    "category": "example",
                    "npm_name": "org.example.ig",
                    "description": "Example IG",
                    "canonical": "http://example.org/ig",
                    "ci_build": "http://example.org/ig/build",
                    "editions": [
                        {
                            "name": "Test",
                            "ig_version": "0.0.1",
                            "package": "org.example.ig#0.0.1",
                            "fhir_version": ["4.0.1"],
                            "url": "http://example.org/ig/0.0.1",
                            "description": "Example IG Release 0.0.1",
                        },
                    ],
                }
            ]
        }

        self.process(setup_data=setup_data, input_data=input_data)

    def test_edition_not_exists(self):
        setup_data = {
            "guides": [
                {
                    "name": "ExampleIG",
                    "category": "example",
                    "npm-name": "org.example.ig",
                    "description": "Example IG",
                    "canonical": "http://example.org/ig",
                    "ci-build": "http://example.org/ig/build",
                    "editions": [],
                }
            ]
        }

        input_data = {
            "title": "Example IG",
            "packageId": "org.example.ig",
            "canonical": "http://example.org/ig",
            "ci-build": "http://example.org/ig/build",
            "sequence": "Test",
            "version": "0.0.1",
            "fhir_version": ["4.0.1"],
            "path": "http://example.org/ig/0.0.1",
            "desc": "Example IG Release 0.0.1",
            "date": "2000-01-01",
            "releaseLabel": "release",
            "publisher": "ExamplePublisher",
        }

        wanted = {
            "guides": [
                {
                    "name": "ExampleIG",
                    "category": "example",
                    "npm_name": "org.example.ig",
                    "description": "Example IG",
                    "canonical": "http://example.org/ig",
                    "ci_build": "http://example.org/ig/build",
                    "editions": [
                        {
                            "name": "Test",
                            "ig_version": "0.0.1",
                            "package": "org.example.ig#0.0.1",
                            "fhir_version": ["4.0.1"],
                            "url": "http://example.org/ig/0.0.1",
                            "description": "Example IG Release 0.0.1",
                        },
                    ],
                }
            ]
        }

        self.process(setup_data=setup_data, input_data=input_data, wanted=wanted)

    def test_edition_exists(self):
        setup_data = {
            "guides": [
                {
                    "name": "ExampleIG",
                    "category": "example",
                    "npm_name": "org.example.ig",
                    "description": "Example IG",
                    "canonical": "http://example.org/ig",
                    "ci_build": "http://example.org/ig/build",
                    "editions": [
                        {
                            "name": "Test",
                            "ig_version": "0.0.1",
                            "package": "org.example.ig#0.0.1",
                            "fhir_version": ["4.0.1"],
                            "url": "http://example.org/ig/0.0.1",
                            "description": "Example IG",
                        },
                    ],
                }
            ]
        }

        input_data = {
            "title": "Example IG",
            "packageId": "org.example.ig",
            "canonical": "http://example.org/ig",
            "ci-build": "http://example.org/ig/build",
            "sequence": "Test",
            "version": "0.0.1",
            "fhir_version": ["4.0.1"],
            "path": "http://example.org/ig/0.0.1",
            "desc": "Example IG",
            "date": "2000-01-01",
            "releaseLabel": "release",
            "publisher": "ExamplePublisher",
        }

        wanted = {
            "guides": [
                {
                    "name": "ExampleIG",
                    "category": "example",
                    "npm_name": "org.example.ig",
                    "description": "Example IG",
                    "canonical": "http://example.org/ig",
                    "ci_build": "http://example.org/ig/build",
                    "editions": [
                        {
                            "name": "Test",
                            "ig_version": "0.0.1",
                            "package": "org.example.ig#0.0.1",
                            "fhir_version": ["4.0.1"],
                            "url": "http://example.org/ig/0.0.1",
                            "description": "Example IG",
                        },
                    ],
                }
            ]
        }

        self.process(setup_data=setup_data, input_data=input_data, wanted=wanted)


def test_list_groups_versions_by_package(version_links):
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
    links = version_links(html).links
    for package in ["one", "two"]:
        assert links[f"https://example.org/{package}/1.10.0"] is False
        assert links[f"https://example.org/{package}/1.9.0"] is True
    assert "<script>unsafe</script>" not in html
    assert 'href="https://example.org/one/1.10.0">1.10.0</a>' in html
    assert '<a class="ig-name"' not in html


def test_package_groups_combine_sequences_and_keep_previews_separate(version_links):
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
    links = version_links(html).links
    for version in ["2.0.0-ballot.2", "2.0.0-rc.2", "3.0.0"]:
        assert links[f"https://example.org/{version}"] is False
    for version in ["1.9.0", "1.10.0", "2.0.0-ballot.1", "2.0.0-rc.1"]:
        assert links[f"https://example.org/{version}"] is True
    assert "Sequence A" in html and "Sequence B" in html
    assert "Ballot" in html and "Release Candidate" in html


def test_legacy_dates_are_ignored_and_older_ballots_collapse(version_links):
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
    links = version_links(html).links
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


def test_multiple_igs_per_package_version_are_preserved(version_links):
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
        links = version_links(html).links
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


def test_empty_list_render():
    with TemporaryDirectory() as directory:
        path = Path(directory)
        ig_list.render(path, IgList())
        assert "Noch keine Pakete" in (path / "index.html").read_text()
