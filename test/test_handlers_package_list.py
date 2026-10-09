from pathlib import Path
from tempfile import TemporaryDirectory

from publish_tools.handlers import ig_history


def test_from_history_includes_current_build(version_links):
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
    assert version_links(html).links["https://example.org/build"] is False
