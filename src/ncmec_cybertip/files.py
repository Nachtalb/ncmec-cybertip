"""The ``<fileDetails>`` document tree and its nested types."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

from pydantic import model_validator
from pydantic_xml import attr, element

from ._flag import Flag
from .common import Base, DeviceId, IpCaptureEvent
from .enums import DetailsType, FileRelevance, IndustryClassification

# Canonical hashType labels for the stdlib algorithms NCMEC commonly expects.
_HASH_TYPE_NAMES = {"md5": "MD5", "sha1": "SHA1", "sha256": "SHA256"}


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

    @classmethod
    def compute(cls, data: bytes, algorithm: str = "md5") -> OriginalFileHash:
        """Build an ``OriginalFileHash`` for ``data`` using a stdlib algorithm.

        Args:
            data: The file bytes to hash.
            algorithm: A :mod:`hashlib` algorithm name (e.g. ``"md5"``,
                ``"sha1"``, ``"sha256"``). The ``hashType`` label is the
                conventional upper-case form (``MD5``/``SHA1``/``SHA256``) for
                known algorithms, otherwise the algorithm name upper-cased.
        """
        digest = hashlib.new(algorithm, data).hexdigest()
        hash_type = _HASH_TYPE_NAMES.get(algorithm.lower(), algorithm.upper())
        return cls(value=digest, hash_type=hash_type)


def file_hashes(
    source: bytes | str | Path | BinaryIO,
    algorithms: Iterable[str] = ("md5", "sha1", "sha256"),
) -> list[OriginalFileHash]:
    """Compute ``OriginalFileHash`` entries for a file, using the standard library.

    Args:
        source: The file to hash -- a path, raw ``bytes``, or an open binary
            file object (read in full).
        algorithms: :mod:`hashlib` algorithm names to compute. Defaults to
            MD5, SHA1, and SHA256.

    Returns:
        One :class:`OriginalFileHash` per algorithm, ready to assign to
        ``FileDetails.original_file_hash``.
    """
    if isinstance(source, (str, Path)):
        data = Path(source).read_bytes()
    elif isinstance(source, bytes):
        data = source
    else:
        data = source.read()
    return [OriginalFileHash.compute(data, algorithm) for algorithm in algorithms]


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

    @model_validator(mode="after")
    def _check_supplemental_reported(self) -> FileDetails:
        """Enforce the documented ``Supplemental Reported`` constraints.

        A file with ``fileRelevance = Supplemental Reported`` may not also carry
        a potential-meme annotation or an industry classification (only
        "Reported" content may be classified or flagged as a potential meme).
        """
        if self.file_relevance is not FileRelevance.SUPPLEMENTAL_REPORTED:
            return self
        if self.industry_classification is not None:
            msg = (
                "industry_classification may not be set when file_relevance is "
                "'Supplemental Reported'"
            )
            raise ValueError(msg)
        if self.file_annotations is not None and (
            self.file_annotations.potential_meme is not None
        ):
            msg = (
                "potential_meme annotation may not be set when file_relevance is "
                "'Supplemental Reported'"
            )
            raise ValueError(msg)
        return self
