"""Server response document types."""

from __future__ import annotations

from pydantic_xml import element

from .common import Base


class ReportResponse(Base, tag="reportResponse"):
    """Response to ``/submit``, ``/upload``, ``/fileinfo``, ``/retract``, ``/status``.

    ``report_id`` is optional: although Appendix D.1 marks it required, the live
    ``/status`` response omits it (it carries only the code and description).
    """

    response_code: int = element(tag="responseCode")
    response_description: str = element(tag="responseDescription")
    report_id: int | None = element(tag="reportId", default=None)
    file_id: str | None = element(tag="fileId", default=None)
    hash: str | None = element(tag="hash", default=None)


class _Files(Base, tag="files"):
    """Wrapper for the list of file IDs in a done response."""

    file_id: list[int] = element(tag="fileId", default_factory=list)


class ReportDoneResponse(Base, tag="reportDoneResponse"):
    """Response to ``/finish``."""

    response_code: int = element(tag="responseCode")
    report_id: int = element(tag="reportId")
    files: _Files = element(default_factory=_Files)

    @property
    def file_ids(self) -> list[int]:
        """The file IDs of files successfully uploaded to the finished report."""
        return self.files.file_id
