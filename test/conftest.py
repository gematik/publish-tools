from html.parser import HTMLParser

import pytest


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


@pytest.fixture
def version_links():
    return VersionLinks
