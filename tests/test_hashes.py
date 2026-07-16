"""Tests for the stdlib hash helpers."""

from __future__ import annotations

import hashlib

from ncmec_cybertip import OriginalFileHash, file_hashes

_DATA = b"hello world"
_MD5 = hashlib.md5(_DATA).hexdigest()
_SHA1 = hashlib.sha1(_DATA).hexdigest()
_SHA256 = hashlib.sha256(_DATA).hexdigest()


def test_compute_defaults_to_md5() -> None:
    h = OriginalFileHash.compute(_DATA)
    assert h.hash_type == "MD5"
    assert h.value == _MD5


def test_compute_named_algorithms() -> None:
    assert OriginalFileHash.compute(_DATA, "sha1").hash_type == "SHA1"
    assert OriginalFileHash.compute(_DATA, "sha256").value == _SHA256


def test_compute_unknown_algorithm_uppercases_label() -> None:
    h = OriginalFileHash.compute(_DATA, "sha512")
    assert h.hash_type == "SHA512"
    assert h.value == hashlib.sha512(_DATA).hexdigest()


def test_file_hashes_defaults_to_three_algorithms_from_bytes() -> None:
    hashes = file_hashes(_DATA)
    assert [h.hash_type for h in hashes] == ["MD5", "SHA1", "SHA256"]
    assert [h.value for h in hashes] == [_MD5, _SHA1, _SHA256]


def test_file_hashes_from_path(tmp_path) -> None:
    f = tmp_path / "e.bin"
    f.write_bytes(_DATA)
    hashes = file_hashes(f, algorithms=["md5"])
    assert len(hashes) == 1
    assert hashes[0].value == _MD5


def test_file_hashes_from_str_path(tmp_path) -> None:
    f = tmp_path / "e.bin"
    f.write_bytes(_DATA)
    assert file_hashes(str(f), algorithms=["sha1"])[0].value == _SHA1


def test_file_hashes_from_file_object(tmp_path) -> None:
    f = tmp_path / "e.bin"
    f.write_bytes(_DATA)
    with f.open("rb") as fh:
        hashes = file_hashes(fh, algorithms=["sha256"])
    assert hashes[0].value == _SHA256


def test_file_hashes_attach_to_file_details() -> None:
    from ncmec_cybertip import FileDetails

    details = FileDetails(
        report_id=1,
        file_id="abc",
        original_file_hash=file_hashes(_DATA),
    )
    parsed = FileDetails.from_xml(details.to_xml(exclude_none=True))
    assert parsed.original_file_hash == details.original_file_hash
