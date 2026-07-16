"""The ``<report>`` document tree and its nested detail types."""

from __future__ import annotations

from datetime import datetime

from pydantic_xml import attr, element

from ._flag import Flag
from .common import (
    Address,
    Base,
    ContactPerson,
    DeviceId,
    Email,
    EstimatedLocation,
    IpCaptureEvent,
    Person,
    Phone,
)
from .enums import (
    AssociatedAccountType,
    BatchedReportReason,
    IncidentType,
)


class ReportAnnotations(Base, tag="reportAnnotations"):
    """Presence-flag tags describing the report."""

    sextortion: Flag = element(tag="sextortion", default=None)
    csam_solicitation: Flag = element(tag="csamSolicitation", default=None)
    minor_to_minor_interaction: Flag = element(
        tag="minorToMinorInteraction", default=None
    )
    spam: Flag = element(tag="spam", default=None)
    sadistic_online_exploitation: Flag = element(
        tag="sadisticOnlineExploitation", default=None
    )
    informational: Flag = element(tag="informational", default=None)


class IncidentSummary(Base, tag="incidentSummary"):
    """General incident information."""

    incident_type: IncidentType = element(tag="incidentType")
    platform: str | None = element(tag="platform", default=None, max_length=256)
    escalate_to_high_priority: str | None = element(
        tag="escalateToHighPriority", default=None, max_length=3000
    )
    report_annotations: ReportAnnotations | None = element(default=None)
    incident_date_time: datetime = element(tag="incidentDateTime")
    incident_date_time_description: str | None = element(
        tag="incidentDateTimeDescription", default=None, max_length=3000
    )


class WebPageIncident(Base, tag="webPageIncident"):
    """Details for an incident that occurred on a web page."""

    third_party_hosted_content: bool | None = attr(
        name="thirdPartyHostedContent", default=None
    )
    url: list[str] = element(tag="url", default_factory=list)
    additional_info: str | None = element(tag="additionalInfo", default=None)


class EmailIncident(Base, tag="emailIncident"):
    """Details for an incident that occurred over email."""

    email_address: list[Email] = element(tag="emailAddress", default_factory=list)
    content: str | None = element(tag="content", default=None)
    additional_info: str | None = element(tag="additionalInfo", default=None)


class NewsgroupIncident(Base, tag="newsgroupIncident"):
    """Details for an incident that occurred in a newsgroup."""

    name: str | None = element(tag="name", default=None, max_length=255)
    email_address: list[Email] = element(tag="emailAddress", default_factory=list)
    content: str | None = element(tag="content", default=None)
    additional_info: str | None = element(tag="additionalInfo", default=None)


class ChatImIncident(Base, tag="chatImIncident"):
    """Details for an incident that occurred over IM or during a chat session."""

    chat_client: str | None = element(tag="chatClient", default=None, max_length=255)
    chat_room_name: str | None = element(
        tag="chatRoomName", default=None, max_length=255
    )
    content: str | None = element(tag="content", default=None)
    additional_info: str | None = element(tag="additionalInfo", default=None)


class OnlineGamingIncident(Base, tag="onlineGamingIncident"):
    """Details for an incident that occurred during an online game."""

    game_name: str | None = element(tag="gameName", default=None, max_length=255)
    console: str | None = element(tag="console", default=None, max_length=255)
    content: str | None = element(tag="content", default=None)
    additional_info: str | None = element(tag="additionalInfo", default=None)


class CellPhoneIncident(Base, tag="cellPhoneIncident"):
    """Details for an incident that occurred primarily via a cell phone."""

    phone_number: Phone | None = element(tag="phoneNumber", default=None)
    latitude: float | None = element(tag="latitude", default=None)
    longitude: float | None = element(tag="longitude", default=None)
    additional_info: str | None = element(tag="additionalInfo", default=None)


class NonInternetIncident(Base, tag="nonInternetIncident"):
    """Details for an incident with no online, computer, or cell-phone component."""

    location_name: str | None = element(
        tag="locationName", default=None, max_length=255
    )
    incident_address: list[Address] = element(
        tag="incidentAddress", default_factory=list
    )
    additional_info: str | None = element(tag="additionalInfo", default=None)


class Peer2PeerIncident(Base, tag="peer2peerIncident"):
    """Details for an incident that occurred via a peer-to-peer network."""

    client: str | None = element(tag="client", default=None, max_length=255)
    ip_capture_event: list[IpCaptureEvent] = element(default_factory=list)
    file_names: str | None = element(tag="fileNames", default=None)
    additional_info: str | None = element(tag="additionalInfo", default=None)


class InternetDetails(Base, tag="internetDetails"):
    """Details of an incident. Exactly one incident sub-element should be supplied."""

    web_page_incident: WebPageIncident | None = element(default=None)
    email_incident: EmailIncident | None = element(default=None)
    newsgroup_incident: NewsgroupIncident | None = element(default=None)
    chat_im_incident: ChatImIncident | None = element(default=None)
    online_gaming_incident: OnlineGamingIncident | None = element(default=None)
    cell_phone_incident: CellPhoneIncident | None = element(default=None)
    non_internet_incident: NonInternetIncident | None = element(default=None)
    peer2peer_incident: Peer2PeerIncident | None = element(default=None)


class LawEnforcement(Base, tag="lawEnforcement"):
    """Law enforcement contact information."""

    flea_country: str | None = attr(name="fleaCountry", default=None)
    agency_name: str = element(tag="agencyName", max_length=255)
    case_number: str | None = element(tag="caseNumber", default=None, max_length=100)
    officer_contact: ContactPerson | None = element(tag="officerContact", default=None)
    reported_to_le: bool | None = element(tag="reportedToLe", default=None)
    served_legal_process_domestic: bool | None = element(
        tag="servedLegalProcessDomestic", default=None
    )
    served_legal_process_international: bool | None = element(
        tag="servedLegalProcessInternational", default=None
    )


class Reporter(Base, tag="reporter"):
    """Information related to the person or company reporting the incident."""

    reporting_person: Person = element(tag="reportingPerson")
    contact_person: ContactPerson | None = element(tag="contactPerson", default=None)
    company_template: str | None = element(tag="companyTemplate", default=None)
    terms_of_service: str | None = element(tag="termsOfService", default=None)
    legal_url: str | None = element(tag="legalURL", default=None, max_length=2083)


class AssociatedAccount(Base, tag="associatedAccount"):
    """An account that a user is associated with."""

    account_type: AssociatedAccountType | None = attr(name="accountType", default=None)
    third_party_user: bool | None = attr(name="thirdPartyUser", default=None)
    platform: str | None = element(tag="platform", default=None, max_length=256)
    first_name: str | None = element(tag="firstName", default=None, max_length=256)
    middle_name: str | None = element(tag="middleName", default=None, max_length=256)
    last_name: str | None = element(tag="lastName", default=None, max_length=256)
    approximate_age: int | None = element(
        tag="approximateAge", default=None, ge=0, le=150
    )
    age_assertion_discrepancy: bool | None = element(
        tag="ageAssertionDiscrepancy", default=None
    )
    phone: list[Phone] = element(tag="phone", default_factory=list)
    email: list[Email] = element(tag="email", default_factory=list)
    all_emails_reported: bool | None = element(tag="allEmailsReported", default=None)
    address: list[Address] = element(tag="address", default_factory=list)
    esp_service: str | None = element(tag="espService", default=None, max_length=256)
    esp_identifier: str | None = element(
        tag="espIdentifier", default=None, max_length=256
    )
    profile_url: list[str] = element(tag="profileUrl", default_factory=list)
    screen_name: str | None = element(tag="screenName", default=None, max_length=256)
    display_name: list[str] = element(tag="displayName", default_factory=list)
    profile_bio: str | None = element(tag="profileBio", default=None)
    group_identifier: str | None = element(
        tag="groupIdentifier", default=None, max_length=256
    )
    ip_capture_event: list[IpCaptureEvent] = element(default_factory=list)
    device_id: list[DeviceId] = element(default_factory=list)
    additional_info: str | None = element(tag="additionalInfo", default=None)


class PersonOrUserReported(Base, tag="personOrUserReported"):
    """A reported user or person involved in the incident (the suspect)."""

    person: Person | None = element(tag="personOrUserReportedPerson", default=None)
    vehicle_description: str | None = element(
        tag="vehicleDescription", default=None, max_length=300
    )
    esp_identifier: str | None = element(
        tag="espIdentifier", default=None, max_length=255
    )
    esp_service: str | None = element(tag="espService", default=None, max_length=100)
    compromised_account: bool | None = element(tag="compromisedAccount", default=None)
    screen_name: str | None = element(tag="screenName", default=None, max_length=256)
    display_name: list[str] = element(tag="displayName", default_factory=list)
    profile_url: list[str] = element(tag="profileUrl", default_factory=list)
    profile_bio: str | None = element(tag="profileBio", default=None)
    ip_capture_event: list[IpCaptureEvent] = element(default_factory=list)
    device_id: list[DeviceId] = element(default_factory=list)
    third_party_user_reported: bool | None = element(
        tag="thirdPartyUserReported", default=None
    )
    prior_ct_reports: list[int] = element(tag="priorCTReports", default_factory=list)
    group_identifier: str | None = element(
        tag="groupIdentifier", default=None, max_length=255
    )
    estimated_location: EstimatedLocation | None = element(default=None)
    all_emails_reported: bool | None = element(tag="allEmailsReported", default=None)
    associated_account: list[AssociatedAccount] = element(default_factory=list)
    additional_info: str | None = element(tag="additionalInfo", default=None)


class IntendedRecipient(Base, tag="intendedRecipient"):
    """An intended recipient involved in the incident."""

    person: Person | None = element(tag="intendedRecipientPerson", default=None)
    esp_identifier: str | None = element(
        tag="espIdentifier", default=None, max_length=255
    )
    esp_service: str | None = element(tag="espService", default=None, max_length=100)
    compromised_account: bool | None = element(tag="compromisedAccount", default=None)
    screen_name: str | None = element(tag="screenName", default=None, max_length=256)
    display_name: list[str] = element(tag="displayName", default_factory=list)
    profile_url: list[str] = element(tag="profileUrl", default_factory=list)
    profile_bio: str | None = element(tag="profileBio", default=None)
    ip_capture_event: list[IpCaptureEvent] = element(default_factory=list)
    device_id: list[DeviceId] = element(default_factory=list)
    prior_ct_reports: list[int] = element(tag="priorCTReports", default_factory=list)
    group_identifier: str | None = element(
        tag="groupIdentifier", default=None, max_length=255
    )
    estimated_location: EstimatedLocation | None = element(default=None)
    all_emails_reported: bool | None = element(tag="allEmailsReported", default=None)
    additional_info: str | None = element(tag="additionalInfo", default=None)


class Victim(Base, tag="victim"):
    """A child victim involved in the incident."""

    person: Person = element(tag="victimPerson")
    esp_identifier: str | None = element(
        tag="espIdentifier", default=None, max_length=255
    )
    esp_service: str | None = element(tag="espService", default=None, max_length=100)
    compromised_account: bool | None = element(tag="compromisedAccount", default=None)
    screen_name: str | None = element(tag="screenName", default=None, max_length=256)
    display_name: list[str] = element(tag="displayName", default_factory=list)
    profile_url: list[str] = element(tag="profileUrl", default_factory=list)
    profile_bio: str | None = element(tag="profileBio", default=None)
    ip_capture_event: list[IpCaptureEvent] = element(default_factory=list)
    device_id: list[DeviceId] = element(default_factory=list)
    school_name: str | None = element(tag="schoolName", default=None, max_length=255)
    prior_ct_reports: list[int] = element(tag="priorCTReports", default_factory=list)
    estimated_location: EstimatedLocation | None = element(default=None)
    all_emails_reported: bool | None = element(tag="allEmailsReported", default=None)
    associated_account: list[AssociatedAccount] = element(default_factory=list)
    additional_info: str | None = element(tag="additionalInfo", default=None)


class BatchedReport(Base, tag="batchedReport"):
    """Indicator that the report concerns multiple reported persons or users."""

    reason: BatchedReportReason = attr(name="reason")


class Report(Base, tag="report"):
    """The root ``<report>`` document used to open a report submission."""

    batched_report: BatchedReport | None = element(default=None)
    incident_summary: IncidentSummary = element()
    internet_details: list[InternetDetails] = element(default_factory=list)
    law_enforcement: LawEnforcement | None = element(default=None)
    reporter: Reporter = element()
    person_or_user_reported: PersonOrUserReported | None = element(default=None)
    intended_recipient: list[IntendedRecipient] = element(default_factory=list)
    victim: list[Victim] = element(default_factory=list)
    additional_info: str | None = element(tag="additionalInfo", default=None)
