from datetime import datetime
from pathlib import Path

from tzlocal import get_localzone

from .. import log
from ..models.ig_info import IgInfo
from ..models.package_feed import PackageDateTime, PackageFeed, PackageGuid, PackageItem

FILE_NAME = "package-feed.xml"


def update(ig_dir: Path, info: IgInfo) -> Path:
    ig_dir.mkdir(parents=True, exist_ok=True)

    now = PackageDateTime(date_time=datetime.now(tz=get_localzone()))

    pkg_info = PackageItem(
        title=f"{info.title} version {info.version}",
        description=info.desc,
        link=f"{info.path}/package.tgz",
        guid=PackageGuid(url=f"{info.path}/package.tgz"),
        creator=info.publisher,
        fhir_version=info.edition.fhir_version[0],
        pub_date=now,
    )

    file = ig_dir / FILE_NAME
    if (feed := read(file)) is None:
        raise Exception("package feed missing, could not update")

    for item in feed.channel.item:
        if item.guid.url == pkg_info.guid.url:
            log.info("no new package, did not update package feed")
            return file

    feed.channel.last_build_date = now
    feed.channel.item.append(pkg_info)

    write(file, feed)
    log.succ("updated package feed")

    return file


def read(file: Path) -> PackageFeed | None:
    if not file.exists():
        return None

    content = file.read_text(encoding="utf-8")
    return PackageFeed.from_xml(content)


def write(file: Path, feed: PackageFeed) -> None:
    content = feed.to_xml(pretty_print=True, skip_empty=True)
    file.write_bytes(content)
