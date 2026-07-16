# ncmec-cybertip

[![CI](https://github.com/Nachtalb/ncmec-cybertip/actions/workflows/ci.yml/badge.svg)](https://github.com/Nachtalb/ncmec-cybertip/actions/workflows/ci.yml)

A fully typed, async Python client for the **NCMEC CyberTipline Reporting API**
(`ispws`), built on [`httpx`](https://www.python-httpx.org/) and
[`pydantic-xml`](https://pydantic-xml.readthedocs.io/).

The CyberTipline API lets Electronic Service Providers (ESPs) submit reports of
apparent child sexual exploitation to the National Center for Missing &
Exploited Children (NCMEC) programmatically, instead of via the web form. This
library wraps all seven endpoints and models the full XML report / file-details
schema as type-checked Python objects.

> The XML documents produced by this library are built from the published
> technical documentation. NCMEC recommends validating submissions against the
> authoritative XSD (`GET /xsd`) — see [Validation](#validation).

## Features

- **Async** client (`httpx.AsyncClient`) covering all endpoints:
  `status`, `xsd`, `submit`, `upload`, `fileinfo`, `finish`, `retract`.
- **Fully typed** report and file-details models (`pydantic-xml`), with field
  validation (lengths, ranges, patterns, enums) mirroring the schema.
- **Presence flags** (`<sextortion/>`, `<viral/>`, …) modeled as plain booleans.
- **Structured errors**: non-zero response codes raise `ApiError` carrying the
  code, description, report ID, and `Request-ID` header.
- Ships with `py.typed`; 100% test coverage; `ruff` + `ty` clean.

## Installation

```bash
uv add ncmec-cybertip
# or
pip install ncmec-cybertip
```

Requires Python 3.13+.

## Quick start

```python
import asyncio
from datetime import datetime, timezone

from ncmec_cybertip import (
    CyberTiplineClient,
    Details,
    Email,
    EventName,
    FileAnnotations,
    FileDetails,
    FileRelevance,
    IncidentSummary,
    IncidentType,
    InternetDetails,
    IpCaptureEvent,
    NameValuePair,
    OriginalFileHash,
    Person,
    Report,
    Reporter,
    TESTING_URL,
    WebPageIncident,
    file_hashes,
)


async def main() -> None:
    report = Report(
        incident_summary=IncidentSummary(
            incident_type=IncidentType.CHILD_PORNOGRAPHY,
            incident_date_time=datetime(2012, 10, 15, 8, tzinfo=timezone.utc),
        ),
        internet_details=[
            InternetDetails(
                web_page_incident=WebPageIncident(url=["http://badsite.example/x"])
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

    async with CyberTiplineClient(
        username="usr123",
        password="pswd123",
        base_url=TESTING_URL,  # omit for production
    ) as client:
        await client.status()                       # verify connectivity + auth

        opened = await client.submit(report)        # 1. open the report
        report_id = opened.report_id

        uploaded = await client.upload(report_id, "evidence.jpg")  # 2. add a file
        file_id = uploaded.file_id

        # 3. optional: attach details/metadata for the uploaded file
        details = FileDetails(
            report_id=report_id,
            file_id=file_id,
            original_file_name="evidence.jpg",
            file_relevance=FileRelevance.REPORTED,
            file_viewed_by_esp=True,
            exif_viewed_by_esp=True,
            file_annotations=FileAnnotations(viral=True, generative_ai=True),
            # Compute MD5 + SHA1 + SHA256 from the file with the standard library,
            # or hand-build OriginalFileHash(value=..., hash_type=...) yourself.
            original_file_hash=file_hashes("evidence.jpg"),
            ip_capture_event=IpCaptureEvent(
                ip_address="63.116.246.17",
                event_name=EventName.UPLOAD,
                date_time=datetime(2011, 10, 31, 12, tzinfo=timezone.utc),
                port=443,
            ),
            details=[
                Details(
                    name_value_pair=[
                        NameValuePair(name="Make", value="Canon"),
                        NameValuePair(name="Model", value="EOS 5D"),
                    ]
                )
            ],
            additional_info=["File was originally posted with 6 others"],
        )
        await client.file_info(details)

        done = await client.finish(report_id)       # 4. finish (files it!)
        print("Filed report", done.report_id, "with files", done.file_ids)


asyncio.run(main())
```

### The report lifecycle

1. `submit(report)` — opens a report, returns the assigned `report_id`.
2. `upload(report_id, file)` — optional, repeatable; returns a `file_id` + MD5.
3. `file_info(file_details)` — optional per file; adds metadata/annotations.
4. `finish(report_id)` — **files the report with NCMEC** (irreversible).
5. `retract(report_id)` — cancels an *unfinished* report.

An unfinished report is automatically deleted by NCMEC 24 hours after it is
opened, or 1 hour after the last modification, whichever is later.

## Authentication

`GET`/`POST` over HTTPS with HTTP Basic auth. Credentials are issued by NCMEC and
differ between the **testing** (`https://exttest.cybertip.org/ispws`) and
**production** (`https://report.cybertip.org/ispws`) environments — exposed as
`TESTING_URL` and `PRODUCTION_URL`. `base_url` defaults to production.

## Error handling

```python
from ncmec_cybertip import ApiError, ResponseCode

try:
    await client.submit(report)
except ApiError as err:
    print(err.response_code)   # e.g. ResponseCode.VALIDATION_FAILED (4100)
    print(err.description)     # server-provided description
    print(err.request_id)      # Request-ID header — include when contacting NCMEC
```

Documented response codes are available as `ResponseCode` constants (the list is
non-exhaustive, so unknown codes still round-trip).

## Uploading files

`upload()` accepts a path, raw `bytes`, or an open binary file object:

```python
await client.upload(report_id, "photo.jpg")             # path
await client.upload(report_id, raw_bytes, filename="x") # bytes
with open("photo.jpg", "rb") as fh:
    await client.upload(report_id, fh, filename="photo.jpg")
```

## File hashes

Original file hashes for `FileDetails` can be computed from the standard library
(`hashlib`) or built by hand. `file_hashes()` accepts a path, `bytes`, or a
binary file object and returns `OriginalFileHash` entries; it defaults to
MD5 + SHA1 + SHA256:

```python
from ncmec_cybertip import OriginalFileHash, file_hashes

details.original_file_hash = file_hashes("evidence.jpg")             # md5, sha1, sha256
details.original_file_hash = file_hashes(raw_bytes, algorithms=["sha256"])

# Single algorithm, or supply a precomputed digest yourself:
OriginalFileHash.compute(raw_bytes, "sha1")
OriginalFileHash(value="fafa5efeaf3cbe3b23b2748d13e629a1", hash_type="MD5")
```

The `hashType` label is the conventional upper-case form (`MD5`/`SHA1`/`SHA256`)
for known algorithms; any other `hashlib` name is upper-cased.

## Industry classification

Files may optionally carry an ESP-designated `IndustryClassification`
(`A1`/`A2`/`B1`/`B2`), where the letter is the apparent age of the minor
(A = prepubescent, B = pubescent) and the digit is the content rank
(1 = sex act, 2 = lascivious exhibition):

```python
from ncmec_cybertip import FileDetails, FileRelevance, IndustryClassification

details = FileDetails(
    report_id=report_id,
    file_id=file_id,
    file_relevance=FileRelevance.REPORTED,
    industry_classification=IndustryClassification.A1,
)
```

Per the schema, only `Reported` content may be classified: setting an
`industry_classification` (or a `potential_meme` annotation) on a
`Supplemental Reported` file raises `ValidationError` locally, before it would
be rejected by NCMEC at `/finish`.

## Bring your own httpx client

Pass an existing `httpx.AsyncClient` (for custom transports, proxies, retries).
When you do, the library will **not** close it for you:

```python
async with httpx.AsyncClient(...) as http:
    client = CyberTiplineClient(username="u", password="p", client=http)
    ...
```

## Validation

Model construction enforces the documented field rules (max lengths, numeric
ranges, regex patterns, enum membership). For authoritative structural
validation, fetch and validate against the live schema:

```python
xsd = await client.get_xsd()
```

## Development

```bash
uv sync
uv run ruff format .
uv run ruff check .
uv run ty check
uv run pytest --cov --cov-fail-under=100
```

### Integration tests

Live tests are marked `integration` and **skip** unless credentials are provided
via environment variables. They are never run by default.

```bash
# Full submit -> retract cycle against the NCMEC TEST environment (exttest).
# Never calls finish(), so nothing is filed.
NCMEC_TEST_USER=... NCMEC_TEST_PASS=... uv run pytest -m integration

# Read-only auth smoke test against PRODUCTION /status (no report is submitted).
NCMEC_PROD_USER=... NCMEC_PROD_PASS=... uv run pytest -m integration \
    tests/test_integration.py::test_status_live_prod
```

## Releasing

Releases are automated via GitHub Actions + PyPI Trusted Publishing (OIDC — no
API tokens). To cut a release:

1. Bump `version` in `pyproject.toml` (e.g. `0.1.0` -> `0.1.1`).
   At the first stable release, also change the `Development Status` classifier
   from `4 - Beta` to `5 - Production/Stable`.
2. Commit, then push a matching tag:

   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

The `Release` workflow then builds the sdist + wheel, verifies the tag matches
the package version, publishes to PyPI, and creates a GitHub Release with
generated notes and the built artifacts attached. A mismatch between the tag and
`pyproject.toml` version fails the build before anything is published.

## Disclaimer

This is an unofficial client and is not affiliated with or endorsed by NCMEC.
Reporting obligations and the meaning of each field are governed by NCMEC's
documentation and applicable law (e.g. 18 U.S.C. § 2258A). Always validate
against the official XSD before submitting in production.

## License

MIT
