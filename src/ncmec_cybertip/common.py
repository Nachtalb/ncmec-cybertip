"""Common element types shared across the report and file-details schemas.

Cardinalities from the schema map to Python types as:

* ``1``      -> required field
* ``0|1``    -> ``T | None`` (default ``None``)
* ``0+``/``1+`` -> ``list[T]`` (default ``[]``)

Field-level ``max_length`` / range validators mirror the documented validation
rules so obviously-invalid payloads fail locally before hitting NCMEC.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import Field
from pydantic_xml import BaseXmlModel, attr, element

from .enums import AddressType, EmailType, EventName, PhoneType


class Base(BaseXmlModel):
    """Base for all schema models.

    Optional elements default to ``None`` and are omitted from output; presence
    flags (empty elements such as ``<sextortion/>``) are preserved. ``skip_empty``
    is deliberately *not* set, as it would strip those meaningful empty elements.
    """


class IpCaptureEvent(Base, tag="ipCaptureEvent"):
    """A capture of an IP address and the event it was captured from."""

    ip_address: str = element(tag="ipAddress")
    event_name: EventName | None = element(tag="eventName", default=None)
    date_time: datetime | None = element(tag="dateTime", default=None)
    possible_proxy: bool | None = element(tag="possibleProxy", default=None)
    port: int | None = element(tag="port", default=None, ge=1, le=65535)


class DeviceId(Base, tag="deviceId"):
    """A capture of a device ID (e.g. IMEI, ICCID, SSID)."""

    id_type: str = element(tag="idType", max_length=255)
    id_value: str = element(tag="idValue", max_length=2083)
    event_name: EventName | None = element(tag="eventName", default=None)
    date_time: datetime | None = element(tag="dateTime", default=None)


class Address(Base, tag="address"):
    """A physical street address."""

    type: AddressType | None = attr(name="type", default=None)
    address: str | None = element(tag="address", default=None, max_length=255)
    city: str | None = element(tag="city", default=None, max_length=100)
    zip_code: str | None = element(tag="zipCode", default=None, max_length=20)
    state: str | None = element(tag="state", default=None)
    non_usa_state: str | None = element(tag="nonUsaState", default=None, max_length=100)
    country: str | None = element(tag="country", default=None)


class Phone(Base, tag="phone"):
    """A phone number."""

    value: str = Field(max_length=50)
    type: PhoneType | None = attr(name="type", default=None)
    verified: bool | None = attr(name="verified", default=None)
    verification_date: datetime | None = attr(name="verificationDate", default=None)
    country_calling_code: str | None = attr(
        name="countryCallingCode", default=None, pattern=r"^\+[0-9]{1,3}$"
    )
    extension: str | None = attr(
        name="extension", default=None, max_length=10, pattern=r"^[0-9]+$"
    )


class Email(Base, tag="email"):
    """An email address."""

    value: str = Field(max_length=255)
    type: EmailType | None = attr(name="type", default=None)
    verified: bool | None = attr(name="verified", default=None)
    verification_date: datetime | None = attr(name="verificationDate", default=None)


class EstimatedLocation(Base, tag="estimatedLocation"):
    """An estimated location for a person or account."""

    verified: bool | None = attr(name="verified", default=None)
    timestamp: datetime | None = attr(name="timestamp", default=None)
    city: str | None = element(tag="city", default=None, max_length=255)
    region: str | None = element(tag="region", default=None, max_length=255)
    country_code: str | None = element(tag="countryCode", default=None)


class Person(Base):
    """A real world person."""

    first_name: str | None = element(tag="firstName", default=None, max_length=100)
    last_name: str | None = element(tag="lastName", default=None, max_length=100)
    phone: list[Phone] = element(tag="phone", default_factory=list)
    email: list[Email] = element(tag="email", default_factory=list)
    address: list[Address] = element(tag="address", default_factory=list)
    age: int | None = element(tag="age", default=None, ge=0, le=150)
    age_assertion_discrepancy: bool | None = element(
        tag="ageAssertionDiscrepancy", default=None
    )
    date_of_birth: date | None = element(tag="dateOfBirth", default=None)


class ContactPerson(Base):
    """A real world person with information pertinent for professional contact."""

    first_name: str | None = element(tag="firstName", default=None, max_length=100)
    last_name: str | None = element(tag="lastName", default=None, max_length=100)
    phone: list[Phone] = element(tag="phone", default_factory=list)
    email: list[Email] = element(tag="email", default_factory=list)
    address: list[Address] = element(tag="address", default_factory=list)
