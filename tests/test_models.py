"""Round-trip and structural tests for the report/file/response models."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

from ncmec_cybertip import (
    Address,
    AddressType,
    AssociatedAccount,
    AssociatedAccountType,
    BatchedReport,
    BatchedReportReason,
    CellPhoneIncident,
    Details,
    DetailsType,
    DeviceId,
    Email,
    EmailType,
    EstimatedLocation,
    EventName,
    FileAnnotations,
    FileDetails,
    FileRelevance,
    IncidentSummary,
    IncidentType,
    IndustryClassification,
    IntendedRecipient,
    InternetDetails,
    IpCaptureEvent,
    LawEnforcement,
    NameValuePair,
    OriginalFileHash,
    Peer2PeerIncident,
    Person,
    PersonOrUserReported,
    Phone,
    PhoneType,
    Report,
    ReportDoneResponse,
    Reporter,
    ReportResponse,
    Victim,
    WebPageIncident,
)
from ncmec_cybertip.report import (
    ChatImIncident,
    EmailIncident,
    NewsgroupIncident,
    NonInternetIncident,
    OnlineGamingIncident,
)


def _canonical(model: Report | FileDetails) -> bytes:
    xml = model.to_xml(exclude_none=True)
    assert isinstance(xml, bytes)
    return xml


# The report XML from section 6.1 of the technical documentation.
EXAMPLE_REPORT_XML = (
    b'<?xml version="1.0" encoding="UTF-8"?>'
    b'<report xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
    b' xsi:noNamespaceSchemaLocation="https://report.cybertip.org/ispws/xsd">'
    b"<incidentSummary>"
    b"<incidentType>Child Pornography (possession, manufacture, "
    b"and distribution)</incidentType>"
    b"<reportAnnotations><sextortion/><csamSolicitation/><minorToMinorInteraction/>"
    b"<spam/><sadisticOnlineExploitation/><informational/></reportAnnotations>"
    b"<incidentDateTime>2012-10-15T08:00:00-07:00</incidentDateTime>"
    b"</incidentSummary>"
    b"<internetDetails><webPageIncident><url>http://badsite.com/baduri.html</url>"
    b"</webPageIncident></internetDetails>"
    b"<reporter><reportingPerson><firstName>John</firstName><lastName>Smith</lastName>"
    b"<email>jsmith@example.com</email></reportingPerson></reporter>"
    b"</report>"
)


def test_example_report_serializes_to_expected_xml(example_report: Report) -> None:
    xml = _canonical(example_report)
    # element structure, not byte-identity (we omit the xsi schema attrs)
    assert b"<incidentType>Child Pornography" in xml
    assert b"<sextortion/>" in xml or b"<sextortion />" in xml
    assert b"<url>http://badsite.com/baduri.html</url>" in xml
    assert b"<email>jsmith@example.com</email>" in xml


def test_example_report_roundtrips(example_report: Report) -> None:
    parsed = Report.from_xml(_canonical(example_report))
    assert parsed == example_report


def test_report_parses_documented_example(example_report: Report) -> None:
    parsed = Report.from_xml(EXAMPLE_REPORT_XML)
    assert parsed.incident_summary.incident_type is IncidentType.CHILD_PORNOGRAPHY
    assert parsed.incident_summary.report_annotations is not None
    assert parsed.incident_summary.report_annotations.spam is not None
    assert parsed.reporter.reporting_person.email[0].value == "jsmith@example.com"


def test_incident_datetime_timezone_preserved() -> None:
    tz = timezone(timedelta(hours=-7))
    dt = datetime(2012, 10, 15, 8, 0, 0, tzinfo=tz)
    summary = IncidentSummary(
        incident_type=IncidentType.CHILD_SEX_TRAFFICKING, incident_date_time=dt
    )
    xml = summary.to_xml(exclude_none=True)
    assert isinstance(xml, bytes)
    assert b"2012-10-15T08:00:00-07:00" in xml
    assert IncidentSummary.from_xml(xml).incident_date_time == dt


def test_full_report_all_sections_roundtrips() -> None:
    report = Report(
        batched_report=BatchedReport(reason=BatchedReportReason.VIRAL_POTENTIAL_MEME),
        incident_summary=IncidentSummary(
            incident_type=IncidentType.ONLINE_ENTICEMENT,
            platform="ExampleApp",
            escalate_to_high_priority="immediate risk",
            incident_date_time=datetime(2020, 1, 1, tzinfo=UTC),
            incident_date_time_description="approximate",
        ),
        internet_details=[
            InternetDetails(
                web_page_incident=WebPageIncident(
                    url=["http://a.example", "http://b.example"],
                    third_party_hosted_content=True,
                    additional_info="note",
                )
            ),
            InternetDetails(
                email_incident=EmailIncident(
                    email_address=[Email(value="bad@example.com")],
                    content="headers",
                )
            ),
            InternetDetails(newsgroup_incident=NewsgroupIncident(name="alt.test")),
            InternetDetails(chat_im_incident=ChatImIncident(chat_client="IRC")),
            InternetDetails(
                online_gaming_incident=OnlineGamingIncident(game_name="Game")
            ),
            InternetDetails(
                cell_phone_incident=CellPhoneIncident(
                    phone_number=Phone(value="5551234", type=PhoneType.MOBILE),
                    latitude=1.5,
                    longitude=-2.5,
                )
            ),
            InternetDetails(
                non_internet_incident=NonInternetIncident(
                    location_name="Somewhere",
                    incident_address=[Address(city="Town", type=AddressType.HOME)],
                )
            ),
            InternetDetails(
                peer2peer_incident=Peer2PeerIncident(
                    client="P2P",
                    ip_capture_event=[
                        IpCaptureEvent(
                            ip_address="1.2.3.4",
                            event_name=EventName.UPLOAD,
                            port=8080,
                            possible_proxy=True,
                        )
                    ],
                    file_names="a.jpg",
                )
            ),
        ],
        law_enforcement=LawEnforcement(
            agency_name="FBI",
            case_number="123",
            reported_to_le=True,
            flea_country="US",
        ),
        reporter=Reporter(
            reporting_person=Person(
                first_name="Jane",
                email=[Email(value="jane@example.com", type=EmailType.WORK)],
                phone=[Phone(value="12345", country_calling_code="+1")],
                address=[Address(country="US", state="NY")],
                age=30,
            ),
            legal_url="https://example.com/legal",
        ),
        person_or_user_reported=PersonOrUserReported(
            person=Person(first_name="Sus"),
            screen_name="baduser",
            display_name=["Bad User"],
            prior_ct_reports=[111, 222],
            device_id=[DeviceId(id_type="IMEI", id_value="990000862471854")],
            estimated_location=EstimatedLocation(city="City", country_code="US"),
            associated_account=[
                AssociatedAccount(
                    account_type=AssociatedAccountType.BILLING,
                    email=[Email(value="billing@example.com")],
                )
            ],
        ),
        intended_recipient=[IntendedRecipient(person=Person(first_name="Target"))],
        victim=[Victim(person=Person(first_name="Child", age=10))],
        additional_info="extra",
    )
    parsed = Report.from_xml(report.to_xml(exclude_none=True))
    assert parsed == report


def test_file_details_roundtrips() -> None:
    details = FileDetails(
        report_id=4564654,
        file_id="b0754af766b426f2928a02c651ed4b99",
        original_file_name="mypic.jpg",
        file_relevance=FileRelevance.REPORTED,
        industry_classification=IndustryClassification.A1,
        file_annotations=FileAnnotations(viral=True, generative_ai=True),
        original_file_hash=[
            OriginalFileHash(value="abc123", hash_type="MD5"),
        ],
        ip_capture_event=IpCaptureEvent(
            ip_address="63.116.246.17", event_name=EventName.UPLOAD
        ),
        details=[
            Details(
                name_value_pair=[
                    NameValuePair(name="Make", value="Canon", type=DetailsType.EXIF)
                ]
            )
        ],
        additional_info=["posted with 6 others"],
    )
    parsed = FileDetails.from_xml(details.to_xml(exclude_none=True))
    assert parsed == details


def test_report_response_parses() -> None:
    xml = (
        b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        b"<reportResponse><responseCode>0</responseCode>"
        b"<responseDescription>Success</responseDescription>"
        b"<reportId>4564654</reportId>"
        b"<fileId>b0754af766b426f2928a02c651ed4b99</fileId>"
        b"<hash>fafa5efeaf3cbe3b23b2748d13e629a1</hash>"
        b"</reportResponse>"
    )
    resp = ReportResponse.from_xml(xml)
    assert resp.response_code == 0
    assert resp.report_id == 4564654
    assert resp.file_id == "b0754af766b426f2928a02c651ed4b99"
    assert resp.hash == "fafa5efeaf3cbe3b23b2748d13e629a1"


def test_report_done_response_exposes_file_ids() -> None:
    # NCMEC returns 32-char hex file IDs (opaque strings), not integers.
    # Regression: report 250799407's real /finish response 502'd because these
    # were previously typed as list[int]. This is the actual production payload.
    xml = (
        b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        b"<reportDoneResponse><responseCode>0</responseCode>"
        b"<reportId>250799407</reportId>"
        b"<files>"
        b"<fileId>3a1d4fd4106b82499b7c93442aa7dca4</fileId>"
        b"<fileId>23eb425911143eadc4987a2b3e221c09</fileId>"
        b"<fileId>abd6aa21e080470e22c4c8c9cb8cf2af</fileId>"
        b"<fileId>01d21d1cc0a6c34885973d6cda08f537</fileId>"
        b"<fileId>d6aed6fe40d471c011640a6781b4a648</fileId>"
        b"<fileId>3c62d4a8c475524b7ecd3f4764eeed94</fileId>"
        b"<fileId>084fe41db96ac651eb0b8b2e0b400de0</fileId>"
        b"</files>"
        b"</reportDoneResponse>"
    )
    done = ReportDoneResponse.from_xml(xml)
    assert done.report_id == 250799407
    assert done.file_ids == [
        "3a1d4fd4106b82499b7c93442aa7dca4",
        "23eb425911143eadc4987a2b3e221c09",
        "abd6aa21e080470e22c4c8c9cb8cf2af",
        "01d21d1cc0a6c34885973d6cda08f537",
        "d6aed6fe40d471c011640a6781b4a648",
        "3c62d4a8c475524b7ecd3f4764eeed94",
        "084fe41db96ac651eb0b8b2e0b400de0",
    ]


def test_report_done_response_empty_files() -> None:
    xml = (
        b"<reportDoneResponse><responseCode>0</responseCode>"
        b"<reportId>99</reportId><files/></reportDoneResponse>"
    )
    done = ReportDoneResponse.from_xml(xml)
    assert done.file_ids == []
