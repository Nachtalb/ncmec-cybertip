"""The ``<fileDetails>`` document tree and its nested types."""

from __future__ import annotations

from datetime import datetime

from pydantic_xml import attr, element

from ._flag import Flag
from .common import Base, DeviceId, IpCaptureEvent
from .enums import DetailsType, FileRelevance, IndustryClassification


class FileAnnotations(Base, tag="fileAnnotations"):
    """Presence-flag tags describing a file."""

    anime_drawing_virtual_hentai: Flag = element(
        tag="animeDrawingVirtualHentai", default=None
    )
    potential_meme: Flag = element(tag="potentialMeme", default=None)
    viral: Flag = element(tag="viral", default=None)
    possible_self_production: Flag = element(tag="possibleSelfProduction", default=None)
    physical_harm: Flag = element(tag="physicalHarm", default=None)
    violence_gore: Flag = element(tag="violenceGore", default=None)
    bestiality: Flag = element(tag="bestiality", default=None)
    live_streaming: Flag = element(tag="liveStreaming", default=None)
    infant: Flag = element(tag="infant", default=None)
    generative_ai: Flag = element(tag="generativeAi", default=None)


class OriginalFileHash(Base, tag="originalFileHash"):
    """An original binary hash value of the file at upload time."""

    value: str
    hash_type: str = attr(name="hashType", max_length=64)


class NameValuePair(Base, tag="nameValuePair"):
    """A single file metadata entry."""

    type: DetailsType | None = attr(name="type", default=None)
    name: str = element(tag="name", max_length=64)
    value: str = element(tag="value")


class Details(Base, tag="details"):
    """Metadata associated with a file."""

    name_value_pair: list[NameValuePair] = element(min_length=1)


class FileDetails(Base, tag="fileDetails"):
    """The root ``<fileDetails>`` document used to supply additional file details."""

    report_id: int = element(tag="reportId")
    file_id: str = element(tag="fileId")
    original_file_name: str | None = element(
        tag="originalFileName", default=None, max_length=2056
    )
    uploaded_to_esp_timestamp: datetime | None = element(
        tag="uploadedToEspTimestamp", default=None
    )
    location_of_file: str | None = element(
        tag="locationOfFile", default=None, max_length=2083
    )
    file_viewed_by_esp: bool | None = element(tag="fileViewedByEsp", default=None)
    exif_viewed_by_esp: bool | None = element(tag="exifViewedByEsp", default=None)
    publicly_available: bool | None = element(tag="publiclyAvailable", default=None)
    file_relevance: FileRelevance | None = element(tag="fileRelevance", default=None)
    file_annotations: FileAnnotations | None = element(default=None)
    industry_classification: IndustryClassification | None = element(
        tag="industryClassification", default=None
    )
    original_file_hash: list[OriginalFileHash] = element(default_factory=list)
    ip_capture_event: IpCaptureEvent | None = element(default=None)
    device_id: list[DeviceId] = element(default_factory=list)
    details: list[Details] = element(default_factory=list)
    additional_info: list[str] = element(tag="additionalInfo", default_factory=list)
