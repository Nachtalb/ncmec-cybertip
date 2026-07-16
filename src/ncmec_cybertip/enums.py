"""Enumerations for the fixed value sets defined by the CyberTipline schema."""

from __future__ import annotations

from enum import StrEnum


class IncidentType(StrEnum):
    """Type of incident being reported (``<incidentType>``)."""

    CHILD_PORNOGRAPHY = "Child Pornography (possession, manufacture, and distribution)"
    CHILD_SEX_TRAFFICKING = "Child Sex Trafficking"
    CHILD_SEX_TOURISM = "Child Sex Tourism"
    CHILD_SEXUAL_MOLESTATION = "Child Sexual Molestation"
    MISLEADING_DOMAIN_NAME = "Misleading Domain Name"
    MISLEADING_WORDS_OR_IMAGES = "Misleading Words or Digital Images on the Internet"
    ONLINE_ENTICEMENT = "Online Enticement of Children for Sexual Acts"
    UNSOLICITED_OBSCENE_MATERIAL = "Unsolicited Obscene Material Sent to a Child"


class EventName(StrEnum):
    """Event from which an IP address or device ID was captured."""

    LOGIN = "Login"
    REGISTRATION = "Registration"
    PURCHASE = "Purchase"
    UPLOAD = "Upload"
    OTHER = "Other"
    UNKNOWN = "Unknown"


class AddressType(StrEnum):
    """Type of a physical address (``type`` attribute)."""

    HOME = "Home"
    BUSINESS = "Business"
    BILLING = "Billing"
    SHIPPING = "Shipping"
    TECHNICAL = "Technical"


class PhoneType(StrEnum):
    """Type of a phone number (``type`` attribute)."""

    MOBILE = "Mobile"
    HOME = "Home"
    BUSINESS = "Business"
    WORK = "Work"
    FAX = "Fax"
    INTERNET = "Internet"
    RECOVERY = "Recovery"


class EmailType(StrEnum):
    """Type of an email address (``type`` attribute)."""

    HOME = "Home"
    WORK = "Work"
    BUSINESS = "Business"
    RECOVERY = "Recovery"


class AssociatedAccountType(StrEnum):
    """Type of an associated account (``accountType`` attribute)."""

    BILLING = "Billing"
    LINKED = "Linked"
    BUSINESS = "Business"
    CREATOR = "Creator"
    PARENT_GUARDIAN = "Parent/Guardian"
    OTHER = "Other"


class FileRelevance(StrEnum):
    """Relevance of a file to the report (``<fileRelevance>``)."""

    REPORTED = "Reported"
    SUPPLEMENTAL_REPORTED = "Supplemental Reported"


class IndustryClassification(StrEnum):
    """ESP-designated categorisation scale (``<industryClassification>``)."""

    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"


class DetailsType(StrEnum):
    """Type of a file metadata entry (``type`` attribute of ``<nameValuePair>``)."""

    EXIF = "EXIF"
    HASH = "HASH"


class BatchedReportReason(StrEnum):
    """Rationale for a batched report (``reason`` attribute of ``<batchedReport>``)."""

    VIRAL_POTENTIAL_MEME = "VIRAL_POTENTIAL_MEME"


class ResponseCode(int):
    """A response code from a submittal. ``0`` is success; any non-zero is an error.

    The documented (non-exhaustive) codes are exposed as class constants. Because
    the list is explicitly non-exhaustive, this is a thin ``int`` subclass rather
    than a closed enum, so unknown codes from the server still round-trip.
    """

    SUCCESS = 0
    SERVER_ERROR = 1000
    SAVE_FAILED = 1100
    UPLOAD_FAILED = 1110
    FILE_UPLOAD_FAILED = 1111
    RESOURCE_NOT_FOUND = 1210
    UPDATE_FAILED = 1300
    AUTHENTICATION_REQUIRED = 2000
    NOT_AUTHORIZED = 3000
    NOT_AUTHORIZED_SUBMISSIONS = 3100
    NOT_AUTHORIZED_UPDATES = 3300
    INVALID_REQUEST = 4000
    VALIDATION_FAILED = 4100
    MALFORMED_XML = 4110
    MALFORMED_FILE = 4200
    REPORT_DOES_NOT_EXIST = 5001
    FILE_DOES_NOT_EXIST = 5002
    REPORT_ALREADY_RETRACTED = 5101
    REPORT_ALREADY_FINISHED = 5102
