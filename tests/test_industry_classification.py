"""Tests for FileDetails industry classification and cross-field rules."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ncmec_cybertip import (
    FileAnnotations,
    FileDetails,
    FileRelevance,
    IndustryClassification,
)


def test_industry_classification_roundtrips() -> None:
    details = FileDetails(
        report_id=1,
        file_id="abc",
        file_relevance=FileRelevance.REPORTED,
        industry_classification=IndustryClassification.B2,
    )
    parsed = FileDetails.from_xml(details.to_xml(exclude_none=True))
    assert parsed.industry_classification is IndustryClassification.B2


@pytest.mark.parametrize(
    "value",
    [
        IndustryClassification.A1,
        IndustryClassification.A2,
        IndustryClassification.B1,
        IndustryClassification.B2,
    ],
)
def test_all_industry_classification_values(value: IndustryClassification) -> None:
    details = FileDetails(report_id=1, file_id="abc", industry_classification=value)
    assert details.industry_classification is value


def test_industry_classification_allowed_when_reported() -> None:
    # Reported is the default relevance; classification is fine.
    details = FileDetails(
        report_id=1,
        file_id="abc",
        industry_classification=IndustryClassification.A1,
    )
    assert details.industry_classification is IndustryClassification.A1


def test_industry_classification_rejected_when_supplemental() -> None:
    with pytest.raises(ValidationError, match="industry_classification may not be set"):
        FileDetails(
            report_id=1,
            file_id="abc",
            file_relevance=FileRelevance.SUPPLEMENTAL_REPORTED,
            industry_classification=IndustryClassification.A1,
        )


def test_potential_meme_rejected_when_supplemental() -> None:
    with pytest.raises(ValidationError, match="potential_meme annotation may not"):
        FileDetails(
            report_id=1,
            file_id="abc",
            file_relevance=FileRelevance.SUPPLEMENTAL_REPORTED,
            file_annotations=FileAnnotations(potential_meme=True),
        )


def test_supplemental_with_other_annotation_allowed() -> None:
    # A non-meme annotation on a Supplemental Reported file is fine.
    details = FileDetails(
        report_id=1,
        file_id="abc",
        file_relevance=FileRelevance.SUPPLEMENTAL_REPORTED,
        file_annotations=FileAnnotations(infant=True),
    )
    assert details.file_annotations is not None
    assert details.file_annotations.infant is not None
