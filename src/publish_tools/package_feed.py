from datetime import datetime
from pathlib import Path

from tzlocal import get_localzone

from .log import log_error, log_info, log_succ
from .models import IgInfo, PackageDateTime, PackageFeed, PackageGuid, PackageItem


def update_package_feed(ig_dir: Path, info: IgInfo) -> Path:
    ig_dir.mkdir(parents=True, exist_ok=True)

    now = PackageDateTime(date_time=datetime.now(tz=get_localzone()))

    pkg_info = PackageItem(
        title=f"{info.name} version {info.edition.ig_version}",
        description=info.edition.description,
        link=f"{info.edition.url}/package.tgz",
        guid=PackageGuid(url=f"{info.edition.url}/package.tgz"),
        creator=info.publisher,
        fhir_version=info.edition.fhir_version[0],
        pub_date=now,
    )

    file = ig_dir / "package-feed.xml"
    if file.exists():
        content = file.read_text(encoding="utf-8")
        feed = PackageFeed.from_xml(content)

        found = False
        for i, item in enumerate(feed.channel.item):
            if item.guid.url == pkg_info.guid.url:
                found = True
                log_info("no new package, did not update package feed")
                return file

        if not found:
            feed.channel.last_build_date = now
            feed.channel.item.append(pkg_info)

            content = feed.to_xml(pretty_print=True, skip_empty=True)
            file.write_bytes(content)

            log_succ("updated package feed")
            return file

    else:
        raise Exception("package feed missing, could not update")
