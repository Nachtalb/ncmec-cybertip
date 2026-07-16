"""Exceptions raised by the CyberTipline client."""

from __future__ import annotations

from .enums import ResponseCode


class CyberTiplineError(Exception):
    """Base class for all errors raised by this library."""


class ApiError(CyberTiplineError):
    """The server returned a non-zero response code.

    Attributes:
        response_code: The numeric response code (see :class:`ResponseCode`).
        description: The human-readable description from the server, if any.
        report_id: The report ID the response related to, if any.
        request_id: The ``Request-ID`` response header, useful for NCMEC support.
    """

    def __init__(
        self,
        response_code: int,
        description: str | None = None,
        report_id: int | None = None,
        request_id: str | None = None,
    ) -> None:
        self.response_code = response_code
        self.description = description
        self.report_id = report_id
        self.request_id = request_id
        detail = description or f"response code {response_code}"
        suffix = f" (Request-ID: {request_id})" if request_id else ""
        super().__init__(f"CyberTipline API error {response_code}: {detail}{suffix}")

    @property
    def is_authentication_error(self) -> bool:
        """Whether the error indicates missing/invalid authentication."""
        return self.response_code == ResponseCode.AUTHENTICATION_REQUIRED
