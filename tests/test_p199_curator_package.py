"""Tests for P199 Curator Submission Packages, Novelty Audit, and Index."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat
import subprocess
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = REPO_ROOT / "docs" / "research" / "p199-curator-packages-index.json"
AUDIT_PATH = REPO_ROOT / "experiments" / "p199-novelty-audit.json"
PACKAGES_DIR = REPO_ROOT / "dist" / "curator-submissions" / "p199"
CURATORS = ["dan_gordon_ljcr", "markus_grassl_codetables", "neil_sloane_oeis"]


def compute_file_sha256(path: Path) -> str:
    """Compute the SHA-256 hex digest of a file on disk."""
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def test_p199_packages_have_all_artifacts() -> None:
    """Test that each P199 curator package contains all required artifacts."""
    assert PACKAGES_DIR.exists(), f"Curator packages dir not found: {PACKAGES_DIR}"

    for curator in CURATORS:
        curator_path = PACKAGES_DIR / curator
        assert curator_path.exists(), f"Package folder missing: {curator_path}"

        # 1. README.md
        readme = curator_path / "README.md"
        assert readme.is_file(), f"README.md missing in {curator}"
        assert len(readme.read_text(encoding="utf-8")) > 50

        # 2. certificate.json OR null-result-notice.md
        has_cert = (curator_path / "certificate.json").is_file()
        has_notice = (curator_path / "null-result-notice.md").is_file()
        assert has_cert or has_notice, f"Neither certificate nor null notice found in {curator}"

        # 3. verify_structured_certificate.py
        verifier = curator_path / "verify_structured_certificate.py"
        assert verifier.is_file(), f"Verifier script missing in {curator}"
        assert bool(verifier.stat().st_mode & stat.S_IXUSR), f"Verifier not executable in {curator}"

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


def test_p199_reproduce_scripts_execute_cleanly() -> None:
    """Test that reproduce.sh runs cleanly offline in under 10 seconds."""
    for curator in CURATORS:
        reproduce_sh = PACKAGES_DIR / curator / "reproduce.sh"
        res = subprocess.run(
            ["bash", str(reproduce_sh)],
            cwd=str(reproduce_sh.parent),
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert res.returncode == 0, f"reproduce.sh failed in {curator}:\n{res.stderr}"
        assert "Verification SUCCESS" in res.stdout or "VERIFIED" in res.stdout


def test_p199_index_matches_disk_hashes() -> None:
    """Test that index JSON exists, lists all packages, and hashes match disk."""
    assert INDEX_PATH.exists(), f"Index file not found: {INDEX_PATH}"

    with INDEX_PATH.open("r", encoding="utf-8") as f:
        index_data = json.load(f)

    assert index_data.get("index_version") == "2.0.0"
    assert index_data.get("overall_campaign_verdict") == "DISCOVERY_TIED"
    packages = index_data.get("curator_packages", {})
    assert set(packages.keys()) == set(CURATORS)

    for curator in CURATORS:
        pkg_data = packages[curator]
        assert "files" in pkg_data
        files_list = pkg_data["files"]
        assert len(files_list) >= 5

        for item in files_list:
            disk_path = REPO_ROOT / item["path"]
            assert disk_path.exists(), f"File listed in index missing on disk: {disk_path}"
            expected_sha = item["sha256"]
            actual_sha = compute_file_sha256(disk_path)
            assert actual_sha == expected_sha, (
                f"Hash mismatch for {disk_path}: index={expected_sha}, disk={actual_sha}"
            )


def test_p199_status_is_pending_human_submission() -> None:
    """Test that all packages are marked pending_human_submission (agent never submits)."""
    with INDEX_PATH.open("r", encoding="utf-8") as f:
        index_data = json.load(f)

    packages = index_data.get("curator_packages", {})
    for curator, pkg in packages.items():
        assert pkg.get("status") == "pending_human_submission", (
            f"Package {curator} has invalid status {pkg.get('status')}; must be pending_human_submission."
        )

    safety = index_data.get("safety_guarantee", {})
    assert safety.get("autonomous_emails_sent") == 0
    assert safety.get("external_api_calls") == 0
    assert safety.get("human_submission_status") == "pending_human_submission"


def test_p199_no_private_emails_in_artifacts() -> None:
    """Test that committed index and scripts do not leak private email addresses."""
    index_text = INDEX_PATH.read_text(encoding="utf-8")
    assert "@gmail.com" not in index_text
    assert "@yahoo.com" not in index_text
    assert "@hotmail.com" not in index_text

    with INDEX_PATH.open("r", encoding="utf-8") as f:
        index_data = json.load(f)

    for cid, pkg in index_data.get("curator_packages", {}).items():
        channel = pkg.get("curator_channel", "")
        assert channel.startswith("http://") or channel.startswith("https://")

    for curator in CURATORS:
        for ext in ["md", "txt"]:
            letter_path = PACKAGES_DIR / curator / f"submission-letter.{ext}"
            content = letter_path.read_text(encoding="utf-8")
            assert "@gmail.com" not in content
            assert "@yahoo.com" not in content
            assert "@hotmail.com" not in content


def test_p199_letters_accurate_and_not_overclaiming() -> None:
    """Test that submission letters make accurate statements without false claims."""
    for curator in CURATORS:
        for ext in ["md", "txt"]:
            letter_path = PACKAGES_DIR / curator / f"submission-letter.{ext}"
            content = letter_path.read_text(encoding="utf-8").lower()

            assert "we broke the record" not in content
            assert "quebramos o recorde" not in content
            assert "new covering design beating" not in content

            if curator == "dan_gordon_ljcr":
                assert "discovery_tied" in content or "tied" in content
                assert "30 blocks" in content
            elif curator == "markus_grassl_codetables":
                assert "gottesman" in content
                assert "negative bound" in content or "cannot achieve" in content
            elif curator == "neil_sloane_oeis":
                assert "a066010" in content
                assert "sqs(10)" in content
