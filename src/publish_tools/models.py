from datetime import datetime
from typing import Optional

from pydantic import AliasChoices, BaseModel, Field
from pydantic_xml import (
    BaseXmlModel,
    attr,
    element,
    xml_field_serializer,
    xml_field_validator,
)
from pydantic_xml.element.element import XmlElementReader, XmlElementWriter

DATETIME_FORMAT = "%a, %d %b %Y %H:%M:%S %z"

NS_ATOM = "http://www.w3.org/2005/Atom"
NS_CONTENT = "http://purl.org/rss/1.0/modules/content/"
NS_DC = "http://purl.org/dc/elements/1.1/"
NS_FHIR = "http://hl7.org/fhir/feed"


class IgDef(BaseModel):
    name: str
    category: str
    npm_name: str = Field(
        serialization_alias="npm-name",
        validation_alias=AliasChoices("npm-name", "npm_name"),
    )
    description: str
    canonical: str
    ci_build: str = Field(
        serialization_alias="ci-build",
        validation_alias=AliasChoices("ci-build", "ci_build"),
    )


class Edition(BaseModel):
    name: str
    ig_version: str = Field(
        serialization_alias="ig-version",
        validation_alias=AliasChoices("ig-version", "ig_version"),
    )
    package: str
    fhir_version: list[str] = Field(
        serialization_alias="fhir-version",
        validation_alias=AliasChoices("fhir_version", "fhir-version"),
    )
    url: str
    description: str


class IgInfo(IgDef):
    edition: Edition


class Guide(IgDef):
    editions: list[Edition]


class IgList(BaseModel):
    guides: list[Guide] = []


######
# Package RSS Feed
######
class PackageDateTime(BaseXmlModel):
    date_time: datetime

    @xml_field_validator("date_time")
    @classmethod
    def validate_datetime(cls, element: XmlElementReader, field_name: str) -> datetime:
        if text := element.pop_text():
            return datetime.strptime(text, DATETIME_FORMAT)

        return datetime.now()

    @xml_field_serializer("date_time")
    def serialize_datetime(
        self, element: XmlElementWriter, value: datetime, field_name: str
    ) -> None:
        sub_element = element.make_element(tag=field_name, nsmap=None)
        sub_element.set_text(value.strftime(DATETIME_FORMAT))

        element.set_text(value.strftime(DATETIME_FORMAT))


class PackageGuid(BaseXmlModel):
    is_perma_link: bool = attr(name="isPermaLink", default=True)
    url: str


class PackageItem(BaseXmlModel, nsmap={"dc": NS_DC, "fhir": NS_FHIR}):
    title: str = element()
    description: str = element()
    link: str = element()
    guid: PackageGuid = element()
    creator: str = element(ns="dc")
    fhir_version: str = element(tag="version", ns="fhir")
    fhir_kind: str = element(tag="kind", ns="fhir", default="IG")
    pub_date: PackageDateTime = element(tag="pubDate")
    details: Optional[str] = element(ns="fhir", default=None)


class PackageLink(BaseXmlModel, ns="atom"):
    href: str = attr()
    rel: str = attr(default="self")
    type: str = attr(default="application/rss+xml")


class PackageChannel(BaseXmlModel, nsmap={"atom": NS_ATOM}):
    title: str = element()
    description: str = element()
    link: str = element()
    generator: str = element()
    last_build_date: PackageDateTime = element(tag="lastBuildDate")
    atom_link: PackageLink = element(tag="link", ns="atom")
    pub_date: PackageDateTime = element(tag="pubDate")
    language: str = element(default="en")
    ttl: int = element(default=600)
    item: list[PackageItem] = element()


class PackageFeed(
    BaseXmlModel,
    tag="rss",
    nsmap={
        "atom": NS_ATOM,
        "content": NS_CONTENT,
        "dc": NS_DC,
        "fhir": NS_FHIR,
    },
):
    channel: PackageChannel = element()
    version: str = attr(default="2.0")
