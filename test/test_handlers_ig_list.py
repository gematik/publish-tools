import json
from pathlib import Path
import tempfile
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

        try:
            input = IgInfoFirst.model_validate(input_data)

            res = ig_list.update(Path(self.tmpdir.name), input)
            res = json.loads(res.model_dump_json())

            diff = DeepDiff(wanted, res)
            self.maxDiff = None
            self.assertDictEqual(diff, {})

        except Exception as e:
            self.fail(e)

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

        self.setupFile(setup_data)

        try:
            input = IgInfoFirst.model_validate(input_data)

            res = ig_list.update(Path(self.tmpdir.name), input)
            res = json.loads(res.model_dump_json())

            diff = DeepDiff(wanted, res)
            self.maxDiff = None
            self.assertDictEqual(diff, {})

        except Exception as e:
            self.fail(e)

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

        self.setupFile(setup_data)

        try:
            input = IgInfo.model_validate(input_data)

            res = ig_list.update(Path(self.tmpdir.name), input)

        except:
            pass

        else:
            self.fail("Expected exception not raised")

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

        self.setupFile(setup_data)

        try:
            input = IgInfo.model_validate(input_data)

            res = ig_list.update(Path(self.tmpdir.name), input)
            res = json.loads(res.model_dump_json())

            diff = DeepDiff(wanted, res)
            self.maxDiff = None
            self.assertDictEqual(diff, {})

        except Exception as e:
            self.fail(e)

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

        self.setupFile(setup_data)

        try:
            input = IgInfo.model_validate(input_data)

            res = ig_list.update(Path(self.tmpdir.name), input)
            res = json.loads(res.model_dump_json())

            diff = DeepDiff(wanted, res)
            self.maxDiff = None
            self.assertDictEqual(diff, {})

        except Exception as e:
            self.fail(e)
