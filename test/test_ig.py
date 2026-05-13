import json
from pathlib import Path
import tempfile
import unittest

from publish_tools import ig
from publish_tools.models.ig_info import IgInfo, IgInfoFirst


class TestGetPackageInformation(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        return super().setUp()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        return super().tearDown()

    def setupFiles(
        self, imp_guide: dict | None, pub_req: dict | None, sushi: dict | None
    ):
        path = Path(self.tmpdir.name)

        if imp_guide:
            imp_guide_file = path / "output" / "ImplementationGuide-org.example.ig.json"
            imp_guide_file.parent.mkdir(parents=True, exist_ok=True)
            imp_guide_file.write_text(json.dumps(imp_guide), "utf-8")

        if pub_req:
            pub_req_file = path / ig.PUB_REQ_FILE
            pub_req_file.parent.mkdir(parents=True, exist_ok=True)
            pub_req_file.write_text(json.dumps(pub_req), "utf-8")

        if sushi:
            sushi_file = path / ig.SUSHI_CONFIG_FILE
            sushi_file.parent.mkdir(parents=True, exist_ok=True)
            sushi_file.write_text(json.dumps(sushi), "utf-8")

    def test_imp_guide_missing(self):
        input_data = {"imp_guide": None, "pub_req": {}, "sushi": {}}
        self.setupFiles(**input_data)

        try:
            ig.get_package_information(Path(self.tmpdir.name))

        except:
            pass

        else:
            self.fail("Expected error not raised")

    def test_pub_req_missing(self):
        input_data = {"imp_guide": {}, "pub_req": None, "sushi": {}}
        self.setupFiles(**input_data)

        try:
            ig.get_package_information(Path(self.tmpdir.name))

        except:
            pass

        else:
            self.fail("Expected error not raised")

    def test_sushi_missing(self):
        input_data = {"imp_guide": {}, "pub_req": {}, "sushi": None}
        self.setupFiles(**input_data)

        try:
            ig.get_package_information(Path(self.tmpdir.name))

        except:
            pass

        else:
            self.fail("Expected error not raised")

    def test_entry_in_imp_guide_missing(self):
        input_data = {
            "imp_guide": {
                "url": "http://example.org/ig/ImplementationGuide/org.example.ig",
                "version": "0.0.1",
                "name": "ImplementationGuide-org.example.ig",
                "title": "Example IG",
                "status": "draft",
                "date": "2020-01-01",
                "publisher": "Example Publisher",
                "copyright": "2020",
                "package_id": "org.example.ig",
                "license": "MIT",
                "fhir_version": ["4.0.1"],
            },
            "pub_req": {
                "package-id": "org.example.ig",
                "version": "0.0.1",
                "path": "http://example.org/ig/0.0.1",
                "status": "draft",
                "first": False,
                "mode": "working",
                "sequence": "STU3",
                "desc": "Example IG",
            },
            "sushi": {"canonical": "http://example.org/ig", "releaseLabel": "draft"},
        }

        wanted = {
            "title": "ImplementationGuide-org.example.ig",
            "package_id": "org.example.ig",
            "canonical": "http://example.org/ig",
            "sequence": "STU3",
            "version": "0.0.1",
            "fhir_version": ["4.0.1"],
            "path": "http://example.org/ig/0.0.1",
            "desc": "Example IG",
            "date": "2020-01-01",
            "release_label": "draft",
            "publisher": "Example Publisher",
        }

        self.setupFiles(**input_data)

        try:
            res = ig.get_package_information(Path(self.tmpdir.name))
            self.assertIsInstance(res, IgInfoFirst)
            res = json.loads(res.model_dump_json(exclude_none=True))

            self.assertDictEqual(wanted, res)

        except:
            pass

        else:
            self.fail("Expected error not raised")

    def test_entry_in_pub_req_missing(self):
        input_data = {
            "imp_guide": {
                "id": "org.example.ig",
                "url": "http://example.org/ig/ImplementationGuide/org.example.ig",
                "version": "0.0.1",
                "name": "ImplementationGuide-org.example.ig",
                "title": "Example IG",
                "status": "draft",
                "date": "2020-01-01",
                "publisher": "Example Publisher",
                "copyright": "2020",
                "package_id": "org.example.ig",
                "license": "MIT",
                "fhir_version": ["4.0.1"],
            },
            "pub_req": {
                "version": "0.0.1",
                "path": "http://example.org/ig/0.0.1",
                "status": "draft",
                "first": False,
                "mode": "working",
                "sequence": "STU3",
                "desc": "Example IG",
            },
            "sushi": {"canonical": "http://example.org/ig", "releaseLabel": "draft"},
        }

        wanted = {
            "title": "ImplementationGuide-org.example.ig",
            "package_id": "org.example.ig",
            "canonical": "http://example.org/ig",
            "sequence": "STU3",
            "version": "0.0.1",
            "fhir_version": ["4.0.1"],
            "path": "http://example.org/ig/0.0.1",
            "desc": "Example IG",
            "date": "2020-01-01",
            "release_label": "draft",
            "publisher": "Example Publisher",
        }

        self.setupFiles(**input_data)

        try:
            res = ig.get_package_information(Path(self.tmpdir.name))
            self.assertIsInstance(res, IgInfoFirst)
            res = json.loads(res.model_dump_json(exclude_none=True))

            self.assertDictEqual(wanted, res)

        except:
            pass

        else:
            self.fail("Expected error not raised")

    def test_entry_in_sushi_missing(self):
        input_data = {
            "imp_guide": {
                "id": "org.example.ig",
                "url": "http://example.org/ig/ImplementationGuide/org.example.ig",
                "version": "0.0.1",
                "name": "ImplementationGuide-org.example.ig",
                "title": "Example IG",
                "status": "draft",
                "date": "2020-01-01",
                "publisher": "Example Publisher",
                "copyright": "2020",
                "package_id": "org.example.ig",
                "license": "MIT",
                "fhir_version": ["4.0.1"],
            },
            "pub_req": {
                "package-id": "org.example.ig",
                "version": "0.0.1",
                "path": "http://example.org/ig/0.0.1",
                "status": "draft",
                "first": False,
                "mode": "working",
                "sequence": "STU3",
                "desc": "Example IG",
            },
            "sushi": {"releaseLabel": "draft"},
        }

        wanted = {
            "title": "ImplementationGuide-org.example.ig",
            "package_id": "org.example.ig",
            "canonical": "http://example.org/ig",
            "sequence": "STU3",
            "version": "0.0.1",
            "fhir_version": ["4.0.1"],
            "path": "http://example.org/ig/0.0.1",
            "desc": "Example IG",
            "date": "2020-01-01",
            "release_label": "draft",
            "publisher": "Example Publisher",
        }

        self.setupFiles(**input_data)

        try:
            res = ig.get_package_information(Path(self.tmpdir.name))
            self.assertIsInstance(res, IgInfoFirst)
            res = json.loads(res.model_dump_json(exclude_none=True))

            self.assertDictEqual(wanted, res)

        except:
            pass

        else:
            self.fail("Expected error not raised")

    def test_first_release(self):
        input_data = {
            "imp_guide": {
                "id": "org.example.ig",
                "url": "http://example.org/ig/ImplementationGuide/org.example.ig",
                "version": "0.0.1",
                "name": "ImplementationGuide-org.example.ig",
                "title": "Example IG",
                "status": "draft",
                "date": "2020-01-01",
                "publisher": "Example Publisher",
                "copyright": "2020",
                "package_id": "org.example.ig",
                "license": "MIT",
                "fhir_version": ["4.0.1"],
            },
            "pub_req": {
                "package-id": "org.example.ig",
                "version": "0.0.1",
                "path": "http://example.org/ig/0.0.1",
                "ci-build": "http://example.org/ig/ci-build",
                "status": "draft",
                "first": True,
                "mode": "working",
                "sequence": "STU3",
                "desc": "Example IG Release 0.0.1",
                "registry-description": "Example IG",
                "registry-country": "Example Country",
                "registry-authority": "Example Authority",
                "category": "Example Category",
                "introduction": "This is a fine IG",
            },
            "sushi": {"canonical": "http://example.org/ig", "releaseLabel": "draft"},
        }

        wanted = {
            "title": "ImplementationGuide-org.example.ig",
            "package_id": "org.example.ig",
            "category": "Example Category",
            "canonical": "http://example.org/ig",
            "ci_build": "http://example.org/ig/ci-build",
            "sequence": "STU3",
            "version": "0.0.1",
            "fhir_version": ["4.0.1"],
            "path": "http://example.org/ig/0.0.1",
            "desc": "Example IG Release 0.0.1",
            "date": "2020-01-01",
            "release_label": "draft",
            "publisher": "Example Publisher",
            "introduction": "This is a fine IG",
        }

        self.setupFiles(**input_data)

        try:
            res = ig.get_package_information(Path(self.tmpdir.name))
            self.assertIsInstance(res, IgInfoFirst)
            res = json.loads(res.model_dump_json(exclude_none=True))

            self.assertDictEqual(wanted, res)

        except Exception as e:
            self.fail(e)

    def test_second_release(self):

        input_data = {
            "imp_guide": {
                "id": "org.example.ig",
                "url": "http://example.org/ig/ImplementationGuide/org.example.ig",
                "version": "0.0.1",
                "name": "ImplementationGuide-org.example.ig",
                "title": "Example IG",
                "status": "draft",
                "date": "2020-01-01",
                "publisher": "Example Publisher",
                "copyright": "2020",
                "package_id": "org.example.ig",
                "license": "MIT",
                "fhir_version": ["4.0.1"],
            },
            "pub_req": {
                "package-id": "org.example.ig",
                "version": "0.0.1",
                "path": "http://example.org/ig/0.0.1",
                "status": "draft",
                "first": False,
                "mode": "working",
                "sequence": "STU3",
                "desc": "Example IG",
            },
            "sushi": {"canonical": "http://example.org/ig", "releaseLabel": "draft"},
        }

        wanted = {
            "title": "ImplementationGuide-org.example.ig",
            "package_id": "org.example.ig",
            "canonical": "http://example.org/ig",
            "sequence": "STU3",
            "version": "0.0.1",
            "fhir_version": ["4.0.1"],
            "path": "http://example.org/ig/0.0.1",
            "desc": "Example IG",
            "date": "2020-01-01",
            "release_label": "draft",
            "publisher": "Example Publisher",
        }

        self.setupFiles(**input_data)

        try:
            res = ig.get_package_information(Path(self.tmpdir.name))
            self.assertIsInstance(res, IgInfo)
            res = json.loads(res.model_dump_json(exclude_none=True))

            self.assertDictEqual(wanted, res)

        except Exception as e:
            self.fail(e)
