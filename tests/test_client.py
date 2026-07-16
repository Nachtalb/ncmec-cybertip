"""Tests for the async client, using respx to mock the HTTP transport."""

from __future__ import annotations

import httpx
import pytest
import respx

from ncmec_cybertip import (
    TESTING_URL,
    ApiError,
    CyberTiplineClient,
    FileDetails,
    Report,
    ResponseCode,
)

BASE = TESTING_URL

_OK_SUBMIT = (
    b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    b"<reportResponse><responseCode>0</responseCode>"
    b"<responseDescription>Success</responseDescription>"
    b"<reportId>4564654</reportId></reportResponse>"
)
_OK_UPLOAD = (
    b"<reportResponse><responseCode>0</responseCode>"
    b"<responseDescription>Success</responseDescription>"
    b"<reportId>4564654</reportId>"
    b"<fileId>b0754af766b426f2928a02c651ed4b99</fileId>"
    b"<hash>fafa5efeaf3cbe3b23b2748d13e629a1</hash></reportResponse>"
)
_OK_FINISH = (
    b"<reportDoneResponse><responseCode>0</responseCode>"
    b"<reportId>4564654</reportId>"
    b"<files><fileId>1</fileId></files></reportDoneResponse>"
)


def _client() -> CyberTiplineClient:
    return CyberTiplineClient(username="usr123", password="pswd123", base_url=BASE)


@respx.mock
async def test_status_success() -> None:
    respx.get(f"{BASE}/status").mock(
        return_value=httpx.Response(
            200,
            content=b"<reportResponse><responseCode>0</responseCode>"
            b"<responseDescription>Remote User : usr123</responseDescription>"
            b"</reportResponse>",
        )
    )
    async with _client() as client:
        resp = await client.status()
    assert resp.response_code == 0
    assert resp.report_id is None  # /status omits reportId
    assert "Remote User" in resp.response_description


@respx.mock
async def test_submit_sends_xml_and_returns_report_id(example_report: Report) -> None:
    route = respx.post(f"{BASE}/submit").mock(
        return_value=httpx.Response(200, content=_OK_SUBMIT)
    )
    async with _client() as client:
        resp = await client.submit(example_report)
    assert resp.report_id == 4564654
    sent = route.calls.last.request
    assert sent.headers["content-type"] == "text/xml; charset=utf-8"
    assert b"<incidentType>Child Pornography" in sent.content
    # exclude_none stripped empty optionals
    assert b"<platform/>" not in sent.content


@respx.mock
async def test_upload_bytes() -> None:
    route = respx.post(f"{BASE}/upload").mock(
        return_value=httpx.Response(200, content=_OK_UPLOAD)
    )
    async with _client() as client:
        resp = await client.upload(4564654, b"\xff\xd8\xff", filename="pic.jpg")
    assert resp.file_id == "b0754af766b426f2928a02c651ed4b99"
    assert resp.hash == "fafa5efeaf3cbe3b23b2748d13e629a1"
    body = route.calls.last.request.content
    assert b"pic.jpg" in body
    assert b'name="id"' in body


@respx.mock
async def test_upload_path(tmp_path) -> None:
    f = tmp_path / "evidence.jpg"
    f.write_bytes(b"\x89PNG\r\n")
    route = respx.post(f"{BASE}/upload").mock(
        return_value=httpx.Response(200, content=_OK_UPLOAD)
    )
    async with _client() as client:
        await client.upload(4564654, f)
    assert b"evidence.jpg" in route.calls.last.request.content


@respx.mock
async def test_upload_file_object(tmp_path) -> None:
    f = tmp_path / "e.bin"
    f.write_bytes(b"data")
    route = respx.post(f"{BASE}/upload").mock(
        return_value=httpx.Response(200, content=_OK_UPLOAD)
    )
    async with _client() as client:
        with f.open("rb") as fh:
            await client.upload(4564654, fh, filename="e.bin")
    assert b"e.bin" in route.calls.last.request.content


@respx.mock
async def test_file_info() -> None:
    respx.post(f"{BASE}/fileinfo").mock(
        return_value=httpx.Response(200, content=_OK_SUBMIT)
    )
    details = FileDetails(report_id=4564654, file_id="abc")
    async with _client() as client:
        resp = await client.file_info(details)
    assert resp.report_id == 4564654


@respx.mock
async def test_finish() -> None:
    route = respx.post(f"{BASE}/finish").mock(
        return_value=httpx.Response(200, content=_OK_FINISH)
    )
    async with _client() as client:
        done = await client.finish(4564654)
    assert done.file_ids == [1]
    assert b"id=4564654" in route.calls.last.request.content


@respx.mock
async def test_retract() -> None:
    respx.post(f"{BASE}/retract").mock(
        return_value=httpx.Response(200, content=_OK_SUBMIT)
    )
    async with _client() as client:
        resp = await client.retract(4564654)
    assert resp.report_id == 4564654


@respx.mock
async def test_get_xsd() -> None:
    respx.get(f"{BASE}/xsd").mock(
        return_value=httpx.Response(200, text="<xsd:schema/>")
    )
    async with _client() as client:
        xsd = await client.get_xsd()
    assert xsd == "<xsd:schema/>"


@respx.mock
async def test_get_xsd_raises_on_http_error() -> None:
    respx.get(f"{BASE}/xsd").mock(return_value=httpx.Response(500))
    async with _client() as client:
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_xsd()


@respx.mock
async def test_nonzero_response_code_raises_api_error() -> None:
    respx.post(f"{BASE}/submit").mock(
        return_value=httpx.Response(
            200,
            content=b"<reportResponse><responseCode>4100</responseCode>"
            b"<responseDescription>Validation failed</responseDescription>"
            b"<reportId>0</reportId></reportResponse>",
            headers={"Request-ID": "req-xyz"},
        )
    )
    report = Report.from_xml(
        b"<report><incidentSummary>"
        b"<incidentType>Child Sex Trafficking</incidentType>"
        b"<incidentDateTime>2020-01-01T00:00:00Z</incidentDateTime>"
        b"</incidentSummary><reporter><reportingPerson>"
        b"<email>a@b.com</email></reportingPerson></reporter></report>"
    )
    async with _client() as client:
        with pytest.raises(ApiError) as excinfo:
            await client.submit(report)
    err = excinfo.value
    assert err.response_code == ResponseCode.VALIDATION_FAILED
    assert err.description == "Validation failed"
    assert err.request_id == "req-xyz"
    assert "req-xyz" in str(err)
    assert not err.is_authentication_error


@respx.mock
async def test_empty_401_raises_auth_error() -> None:
    respx.get(f"{BASE}/status").mock(return_value=httpx.Response(401, content=b""))
    async with _client() as client:
        with pytest.raises(ApiError) as excinfo:
            await client.status()
    assert excinfo.value.is_authentication_error is False  # http 401, not app 2000
    assert excinfo.value.response_code == 401


@respx.mock
async def test_app_auth_required_code_flags_auth_error() -> None:
    respx.get(f"{BASE}/status").mock(
        return_value=httpx.Response(
            200,
            content=b"<reportResponse><responseCode>2000</responseCode>"
            b"<responseDescription>Authentication required</responseDescription>"
            b"<reportId>0</reportId></reportResponse>",
        )
    )
    async with _client() as client:
        with pytest.raises(ApiError) as excinfo:
            await client.status()
    assert excinfo.value.is_authentication_error


async def test_client_uses_injected_httpx_client() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, content=_OK_SUBMIT)
    )
    async with httpx.AsyncClient(transport=transport) as http:
        client = CyberTiplineClient(
            username="u", password="p", base_url=BASE, client=http
        )
        resp = await client.retract(1)
        await client.aclose()  # must NOT close the injected client
    assert resp.report_id == 4564654
    assert http.is_closed  # closed by the `async with`, not by aclose()


def test_base_url_trailing_slash_stripped() -> None:
    client = CyberTiplineClient(username="u", password="p", base_url=f"{BASE}/")
    assert client._base_url == BASE
