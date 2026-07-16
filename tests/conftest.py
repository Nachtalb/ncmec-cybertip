"""Shared fixtures and the canonical example payloads from the NCMEC docs."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from ncmec_cybertip import (
    Email,
    IncidentSummary,
    IncidentType,
    InternetDetails,
    Person,
    Report,
    ReportAnnotations,
    Reporter,
    WebPageIncident,
)


@pytest.fixture
def example_report() -> Report:
    """The section 6.1 example report, constructed via the typed models."""
    tz = timezone(timedelta(hours=-7))
    return Report(
        incident_summary=IncidentSummary(
            incident_type=IncidentType.CHILD_PORNOGRAPHY,
            report_annotations=ReportAnnotations(
                sextortion=True,
                csam_solicitation=True,
                minor_to_minor_interaction=True,
                spam=True,
                sadistic_online_exploitation=True,
                informational=True,
            ),
            incident_date_time=datetime(2012, 10, 15, 8, 0, 0, tzinfo=tz),
        ),
        internet_details=[
            InternetDetails(
                web_page_incident=WebPageIncident(
                    url=["http://badsite.com/baduri.html"]
                )
            )
        ],
        reporter=Reporter(
            reporting_person=Person(
                first_name="John",
                last_name="Smith",
                email=[Email(value="jsmith@example.com")],
            )
        ),
    )
