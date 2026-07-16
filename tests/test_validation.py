"""Tests that documented field validation rules are enforced locally."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ncmec_cybertip import (
    Email,
    IpCaptureEvent,
    OriginalFileHash,
    Person,
    Phone,
)
from ncmec_cybertip.enums import ResponseCode


def test_ip_port_range_rejected() -> None:
    with pytest.raises(ValidationError):
        IpCaptureEvent(ip_address="1.2.3.4", port=70000)


def test_ip_port_range_accepted() -> None:
    assert IpCaptureEvent(ip_address="1.2.3.4", port=443).port == 443


def test_person_age_range_rejected() -> None:
    with pytest.raises(ValidationError):
        Person(age=200)


def test_email_max_length_rejected() -> None:
    with pytest.raises(ValidationError):
        Email(value="a" * 256 + "@example.com")


def test_phone_country_calling_code_pattern() -> None:
    assert Phone(value="123", country_calling_code="+41").country_calling_code == "+41"
    with pytest.raises(ValidationError):
        Phone(value="123", country_calling_code="0041")


def test_phone_extension_pattern() -> None:
    with pytest.raises(ValidationError):
        Phone(value="123", extension="x12")


def test_original_file_hash_type_max_length() -> None:
    with pytest.raises(ValidationError):
        OriginalFileHash(value="deadbeef", hash_type="X" * 65)


def test_response_code_constants() -> None:
    assert ResponseCode.SUCCESS == 0
    assert ResponseCode.VALIDATION_FAILED == 4100
    assert ResponseCode.REPORT_ALREADY_FINISHED == 5102
    # non-exhaustive: unknown codes remain valid ints
    assert int(ResponseCode(9999)) == 9999
