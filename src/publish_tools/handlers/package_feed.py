from datetime import datetime
from pathlib import Path

from tzlocal import get_localzone

from .. import log
from ..models.ig_info import IgInfo
from ..models.package_feed import PackageDateTime, PackageFeed, PackageGuid, PackageItem
from .helper import read_xml, write_xml

FILE_NAME = "package-feed.xml"


def update(ig_dir: Path, info: IgInfo) -> PackageFeed:
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

    if (feed := read_xml(ig_dir, FILE_NAME, PackageFeed)) is None:
        raise Exception("package feed missing, could not update")

    for item in feed.channel.item:
        if item.guid.url == pkg_info.guid.url:
            log.info("no new package, did not update package feed")
            return feed

    feed.channel.last_build_date = now
    feed.channel.item.append(pkg_info)

    write_xml(ig_dir, FILE_NAME, feed)
    log.succ("updated package feed")

    return feed
