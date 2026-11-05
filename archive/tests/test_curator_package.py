"""Tests for P187 Curator Submission Packages and Index."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import stat
import pytest

INDEX_PATH = Path("docs/research/p187-curator-packages-index.json")
AUDIT_PATH = Path("experiments/p186-novelty-audit.json")
PACKAGES_DIR = Path("dist/curator-submissions")
CURATORS = ["ljcr_gordon", "grassl_codetables", "oeis_editors"]


def compute_file_sha256(path: Path) -> str:
    """Compute the SHA-256 hex digest of a file on disk."""
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def test_package_has_all_artifacts() -> None:
    """Test that each curator package contains all 6 required artifacts."""
    assert PACKAGES_DIR.exists(), f"Curator packages dir not found: {PACKAGES_DIR}"

    for curator in CURATORS:
        curator_path = PACKAGES_DIR / curator
        assert curator_path.exists(), f"Package folder missing: {curator_path}"

        # 1. README.md
        assert (curator_path / "README.md").is_file(), f"README.md missing in {curator}"

        # 2. certificate.json OR null-result-notice.md
        has_cert = (curator_path / "certificate.json").is_file()
        has_notice = (curator_path / "null-result-notice.md").is_file()
        assert has_cert or has_notice, f"Neither certificate nor null notice found in {curator}"

        # 3. verify_frontier_certificate.py
        verifier = curator_path / "verify_frontier_certificate.py"
        assert verifier.is_file(), f"Verifier script missing in {curator}"

        # 4. reproduce.sh (must be executable)
        reproduce = curator_path / "reproduce.sh"
        assert reproduce.is_file(), f"reproduce.sh missing in {curator}"
        assert bool(reproduce.stat().st_mode & stat.S_IXUSR), (
            f"reproduce.sh not executable in {curator}"
        )

        # 5. submission-letter.md
        assert (curator_path / "submission-letter.md").is_file(), (
            f"submission-letter.md missing in {curator}"
        )

        # 6. submission-letter.txt
        assert (curator_path / "submission-letter.txt").is_file(), (
            f"submission-letter.txt missing in {curator}"
        )


def test_index_matches_disk_hashes() -> None:
    """Test that the index JSON exists, lists all packages, and hashes match disk."""
    assert INDEX_PATH.exists(), f"Index file not found: {INDEX_PATH}"

    with INDEX_PATH.open("r", encoding="utf-8") as f:
        index_data = json.load(f)

    assert index_data.get("phase") == "P187"
    packages = index_data.get("packages", {})
    assert set(packages.keys()) == set(CURATORS)

    for curator in CURATORS:
        pkg_data = packages[curator]
        assert "files" in pkg_data
        files_list = pkg_data["files"]
        assert len(files_list) >= 6

        for item in files_list:
            disk_path = Path(item["path"])
            assert disk_path.exists(), f"File listed in index missing on disk: {disk_path}"
            expected_sha = item["sha256"]
            actual_sha = compute_file_sha256(disk_path)
            assert actual_sha == expected_sha, (
                f"Hash mismatch for {disk_path}: index={expected_sha}, disk={actual_sha}"
            )


def test_letters_make_no_unchecked_claims() -> None:
    """Test that submission letters make no unchecked discovery claims without CONFIRMED verdict."""
    with AUDIT_PATH.open("r", encoding="utf-8") as f:
        audit_data = json.load(f)

    confirmed_count = audit_data.get("summary", {}).get("confirmed", 0)

    # Scrutinize all letter files in each curator package
    words_requiring_confirmed = ["novo", "new", "record", "quebramos"]

    for curator in CURATORS:
        for ext in ["md", "txt"]:
            letter_path = PACKAGES_DIR / curator / f"submission-letter.{ext}"
            content = letter_path.read_text(encoding="utf-8")
            lower_content = content.lower()

            # Affirmative claims of discovery are strictly forbidden
            assert "quebramos o recorde" not in lower_content
            assert "we broke the record" not in lower_content
            assert "new record discovered" not in lower_content
            assert "new covering design beating" not in lower_content

            # If any of the tracked words appears, check that CONFIRMED is cited
            contains_tracked_word = any(w in lower_content for w in words_requiring_confirmed)
            if contains_tracked_word:
                assert "confirmed" in lower_content, (
                    f"Letter in {curator} uses tracked words without referencing CONFIRMED: {letter_path}"
                )

            # When confirmed_count == 0, check explicit null result disclaimers
            if confirmed_count == 0:
                assert (
                    "null_result" in lower_content
                    or "null result" in lower_content
                    or "null-result" in lower_content
                ), f"Letter in {curator} lacks null result declaration: {letter_path}"
                assert "not claim" in lower_content or "not claimed" in lower_content, (
                    f"Letter in {curator} lacks explicit non-claim disclaimer: {letter_path}"
                )


def test_status_is_pending_human() -> None:
    """Test that all packages are marked pending_human_submission (agent never submits)."""
    with INDEX_PATH.open("r", encoding="utf-8") as f:
        index_data = json.load(f)

    packages = index_data.get("packages", {})
    for curator, pkg in packages.items():
        assert pkg.get("status") == "pending_human_submission", (
            f"Package {curator} has invalid status {pkg.get('status')}; "
            "must be pending_human_submission."
        )


def test_no_private_emails_in_artifacts() -> None:
    """Test that committed index and scripts do not leak private email addresses."""
    # Ensure no personal emails (e.g. gmail, yahoo, or raw @ addresses) in index
    index_text = INDEX_PATH.read_text(encoding="utf-8")
    assert "@gmail.com" not in index_text
    assert "@yahoo.com" not in index_text
    assert "@hotmail.com" not in index_text

    # Check that curator channels use public URLs
    with INDEX_PATH.open("r", encoding="utf-8") as f:
        index_data = json.load(f)

    for cid, pkg in index_data.get("packages", {}).items():
        channel = pkg.get("curator_channel", "")
        assert channel.startswith("http://") or channel.startswith("https://")
