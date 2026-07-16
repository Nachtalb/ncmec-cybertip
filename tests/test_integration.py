"""Live integration tests against the NCMEC test environment.

These are skipped unless valid NCMEC-issued API credentials are supplied via the
``NCMEC_TEST_USER`` and ``NCMEC_TEST_PASS`` environment variables. They run
against :data:`ncmec_cybertip.TESTING_URL` (``exttest.cybertip.org``).

Run them explicitly with::

    NCMEC_TEST_USER=... NCMEC_TEST_PASS=... uv run pytest -m integration

The example ``usr123``/``pswd123`` credentials from the documentation are for
illustration only and will not authenticate.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime

import pytest

from ncmec_cybertip import (
    PRODUCTION_URL,
    TESTING_URL,
    CyberTiplineClient,
    Email,
    IncidentSummary,
    IncidentType,
    InternetDetails,
    Person,
    Report,
    Reporter,
    WebPageIncident,
)

pytestmark = pytest.mark.integration

_USER = os.environ.get("NCMEC_TEST_USER")
_PASS = os.environ.get("NCMEC_TEST_PASS")
_PROD_USER = os.environ.get("NCMEC_PROD_USER")
_PROD_PASS = os.environ.get("NCMEC_PROD_PASS")

_skip = pytest.mark.skipif(
    not (_USER and _PASS),
    reason="set NCMEC_TEST_USER and NCMEC_TEST_PASS to run live integration tests",
)
_skip_prod = pytest.mark.skipif(
    not (_PROD_USER and _PROD_PASS),
    reason="set NCMEC_PROD_USER and NCMEC_PROD_PASS to run the prod status smoke test",
)


def _make_client() -> CyberTiplineClient:
    assert _USER is not None
    assert _PASS is not None
    return CyberTiplineClient(username=_USER, password=_PASS, base_url=TESTING_URL)


def _sample_report() -> Report:
    return Report(
        incident_summary=IncidentSummary(
            incident_type=IncidentType.CHILD_PORNOGRAPHY,
            incident_date_time=datetime(2020, 1, 1, tzinfo=UTC),
        ),
        internet_details=[
            InternetDetails(
                web_page_incident=WebPageIncident(url=["http://example.com/x"])
            )
        ],
        reporter=Reporter(
            reporting_person=Person(email=[Email(value="reporter@example.com")])
        ),
    )


@_skip
async def test_status_live() -> None:
    async with _make_client() as client:
        resp = await client.status()
    assert resp.response_code == 0


@_skip_prod
async def test_status_live_prod() -> None:
    """Read-only auth smoke test against production. Never submits a report."""
    assert _PROD_USER is not None
    assert _PROD_PASS is not None
    async with CyberTiplineClient(
        username=_PROD_USER, password=_PROD_PASS, base_url=PRODUCTION_URL
    ) as client:
        resp = await client.status()
    assert resp.response_code == 0


@_skip
async def test_full_submit_retract_cycle_live() -> None:
    """Open a report then retract it, so nothing is actually filed with NCMEC."""
    async with _make_client() as client:
        submitted = await client.submit(_sample_report())
        assert submitted.report_id is not None
        assert submitted.report_id > 0
        retracted = await client.retract(submitted.report_id)
        assert retracted.report_id == submitted.report_id
