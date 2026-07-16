"""Async client for the NCMEC CyberTipline Reporting API."""

from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import BinaryIO

import httpx

from .exceptions import ApiError
from .files import FileDetails
from .report import Report
from .responses import ReportDoneResponse, ReportResponse

#: Production base URI.
PRODUCTION_URL = "https://report.cybertip.org/ispws"
#: NCMEC-provided testing environment base URI.
TESTING_URL = "https://exttest.cybertip.org/ispws"

_XML_HEADERS = {"Content-Type": "text/xml; charset=utf-8"}


class CyberTiplineClient:
    """Async client wrapping the seven CyberTipline Reporting API endpoints.

    Use as an async context manager::

        async with CyberTiplineClient(username="u", password="p") as client:
            await client.status()
            resp = await client.submit(report)
            report_id = resp.report_id

    Args:
        username: NCMEC-provided username.
        password: NCMEC-provided password.
        base_url: API base URI. Defaults to the production environment; pass
            :data:`TESTING_URL` for the NCMEC test environment.
        client: An existing :class:`httpx.AsyncClient` to use. When omitted, one
            is created and owned (closed on exit) by this instance.
        timeout: Request timeout in seconds (ignored when ``client`` is given).
    """

    def __init__(
        self,
        *,
        username: str,
        password: str,
        base_url: str = PRODUCTION_URL,
        client: httpx.AsyncClient | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            auth=(username, password), timeout=timeout
        )

    async def __aenter__(self) -> CyberTiplineClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying HTTP client if this instance owns it."""
        if self._owns_client:
            await self._client.aclose()

    # -- endpoints ---------------------------------------------------------

    async def status(self) -> ReportResponse:
        """``GET /status`` -- verify connectivity and authentication."""
        response = await self._client.get(f"{self._base_url}/status")
        return self._parse(response, ReportResponse)

    async def get_xsd(self) -> str:
        """``GET /xsd`` -- download the latest XML schema definition."""
        response = await self._client.get(f"{self._base_url}/xsd")
        response.raise_for_status()
        return response.text

    async def submit(self, report: Report) -> ReportResponse:
        """``POST /submit`` -- open a report submission.

        Returns the response carrying the assigned ``report_id``.
        """
        response = await self._client.post(
            f"{self._base_url}/submit",
            content=report.to_xml(
                encoding="utf-8", xml_declaration=True, exclude_none=True
            ),
            headers=_XML_HEADERS,
        )
        return self._parse(response, ReportResponse)

    async def upload(
        self,
        report_id: int,
        file: BinaryIO | bytes | str | Path,
        *,
        filename: str = "file",
    ) -> ReportResponse:
        """``POST /upload`` -- upload a file to an open report.

        Args:
            report_id: The report ID to associate the file with.
            file: The file to upload -- a path, raw bytes, or an open binary
                file object.
            filename: Filename to send in the multipart body (used when ``file``
                is bytes or a file object; a path's own name takes precedence).

        Returns the response carrying the assigned ``file_id`` and MD5 ``hash``.
        """
        content: bytes | BinaryIO
        if isinstance(file, (str, Path)):
            path = Path(file)
            content = path.read_bytes()
            filename = path.name
        else:
            content = file
        response = await self._client.post(
            f"{self._base_url}/upload",
            data={"id": str(report_id)},
            files={"file": (filename, content)},
        )
        return self._parse(response, ReportResponse)

    async def file_info(self, details: FileDetails) -> ReportResponse:
        """``POST /fileinfo`` -- supply additional details for an uploaded file."""
        response = await self._client.post(
            f"{self._base_url}/fileinfo",
            content=details.to_xml(
                encoding="utf-8", xml_declaration=True, exclude_none=True
            ),
            headers=_XML_HEADERS,
        )
        return self._parse(response, ReportResponse)

    async def finish(self, report_id: int) -> ReportDoneResponse:
        """``POST /finish`` -- finish a report submission.

        After a report is finished no more files/details can be added and it can
        no longer be cancelled.
        """
        response = await self._client.post(
            f"{self._base_url}/finish", data={"id": str(report_id)}
        )
        return self._parse(response, ReportDoneResponse)

    async def retract(self, report_id: int) -> ReportResponse:
        """``POST /retract`` -- cancel a report before it is finished."""
        response = await self._client.post(
            f"{self._base_url}/retract", data={"id": str(report_id)}
        )
        return self._parse(response, ReportResponse)

    # -- internals ---------------------------------------------------------

    def _parse[T: ReportResponse | ReportDoneResponse](
        self, response: httpx.Response, model: type[T]
    ) -> T:
        """Parse an XML response body and raise :class:`ApiError` on failure."""
        request_id = response.headers.get("Request-ID")
        if response.status_code >= 400 and not response.content:
            # Auth failures return an empty body with a 401 and no XML.
            raise ApiError(
                response.status_code,
                description=response.reason_phrase or None,
                request_id=request_id,
            )
        parsed = model.from_xml(response.content)
        if parsed.response_code != 0:
            description = getattr(parsed, "response_description", None)
            raise ApiError(
                parsed.response_code,
                description=description,
                report_id=parsed.report_id,
                request_id=request_id,
            )
        return parsed
