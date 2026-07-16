"""Tests for presence-flag empty elements (``Flag``)."""

from __future__ import annotations

import pytest
from pydantic_xml import BaseXmlModel

from ncmec_cybertip import ReportAnnotations
from ncmec_cybertip.files import FileAnnotations


def _xml(model: BaseXmlModel) -> bytes:
    out = model.to_xml(exclude_none=True)
    assert isinstance(out, bytes)
    return out


def test_flag_true_emits_empty_element() -> None:
    xml = _xml(ReportAnnotations(sextortion=True))
    assert b"<sextortion" in xml
    assert b"<spam" not in xml


def test_flag_false_omits_element() -> None:
    assert b"<sextortion" not in _xml(ReportAnnotations(sextortion=False))


def test_flag_default_omits_element() -> None:
    assert _xml(ReportAnnotations()) in (
        b"<reportAnnotations/>",
        b"<reportAnnotations />",
    )


def test_flag_parses_presence_as_truthy() -> None:
    xml = b"<reportAnnotations><sextortion/><spam/></reportAnnotations>"
    ann = ReportAnnotations.from_xml(xml)
    assert ann.sextortion is not None
    assert ann.spam is not None
    assert ann.informational is None


def test_flag_roundtrip_preserves_set_flags() -> None:
    original = FileAnnotations(viral=True, potential_meme=True, infant=False)
    parsed = FileAnnotations.from_xml(_xml(original))
    assert parsed.viral is not None
    assert parsed.potential_meme is not None
    assert parsed.infant is None


def test_flag_rejects_non_bool() -> None:
    with pytest.raises((TypeError, ValueError)):
        ReportAnnotations(sextortion="yes")  # type: ignore[arg-type]
