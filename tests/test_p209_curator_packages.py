"""Tests for P209 Curator Submission Packages, Novelty Audit, and Index."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = REPO_ROOT / "docs" / "research" / "p209-curator-packages-index.json"
PACKAGES_DIR = REPO_ROOT / "dist" / "curator-submissions" / "p209"
CURATORS = ["markus_grassl_codetables", "dan_gordon_ljcr", "neil_sloane_oeis"]


def compute_file_sha256(path: Path) -> str:
    """Compute the SHA-256 hex digest of a file on disk."""
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def test_p209_packages_have_all_artifacts() -> None:
    """Test that each P209 curator package contains all required artifacts."""
    assert PACKAGES_DIR.exists(), f"Curator packages dir not found: {PACKAGES_DIR}"

    for curator in CURATORS:
        curator_path = PACKAGES_DIR / curator
        assert curator_path.exists(), f"Package folder missing: {curator_path}"

        # 1. README.md
        readme = curator_path / "README.md"
        assert readme.is_file(), f"README.md missing in {curator}"
        assert len(readme.read_text(encoding="utf-8")) > 50

        # 2. At least one certificate JSON file
        cert_files = list(curator_path.glob("*.json"))
        assert len(cert_files) >= 1, f"No certificate JSON found in {curator}"

        # 3. verify_generalized_certificate.py
        verifier = curator_path / "verify_generalized_certificate.py"
        assert verifier.is_file(), f"Verifier script missing in {curator}"
        assert bool(verifier.stat().st_mode & stat.S_IXUSR), f"Verifier not executable in {curator}"

        # 4. reproduce.sh (must be executable)
        reproduce = curator_path / "reproduce.sh"
        assert reproduce.is_file(), f"reproduce.sh missing in {curator}"
        assert bool(reproduce.stat().st_mode & stat.S_IXUSR), (
            f"reproduce.sh not executable in {curator}"
        )

        # 5. submission-letter.md
        sub_md = curator_path / "submission-letter.md"
        assert sub_md.is_file(), f"submission-letter.md missing in {curator}"
        assert len(sub_md.read_text(encoding="utf-8")) > 50

        # 6. submission-letter.txt
        sub_txt = curator_path / "submission-letter.txt"
        assert sub_txt.is_file(), f"submission-letter.txt missing in {curator}"
        assert len(sub_txt.read_text(encoding="utf-8")) > 50


def test_p209_reproduce_scripts_execute_cleanly() -> None:
    """Test that reproduce.sh runs cleanly offline in under 5 seconds."""
    for curator in CURATORS:
        reproduce_sh = PACKAGES_DIR / curator / "reproduce.sh"
        res = subprocess.run(
            ["bash", str(reproduce_sh)],
            cwd=str(reproduce_sh.parent),
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert res.returncode == 0, f"reproduce.sh failed in {curator}:\n{res.stderr}\n{res.stdout}"
        assert "Verification SUCCESS" in res.stdout or "ALL PASSED" in res.stdout


def test_p209_index_matches_disk_hashes() -> None:
    """Test that index JSON exists, lists all packages, and hashes match disk."""
    assert INDEX_PATH.exists(), f"Index file not found: {INDEX_PATH}"

    with INDEX_PATH.open("r", encoding="utf-8") as f:
        index_data = json.load(f)

    assert index_data.get("index_version") == "3.0.0"
    assert index_data.get("overall_campaign_verdict") == "DISCOVERY_TIED"
    packages = index_data.get("curator_packages", {})
    assert set(packages.keys()) == set(CURATORS)

    for curator in CURATORS:
        pkg_data = packages[curator]
        assert "files" in pkg_data
        files_list = pkg_data["files"]
        assert len(files_list) >= 5

        for item in files_list:
            disk_file = REPO_ROOT / item["path"]
            assert disk_file.is_file(), f"File {item['path']} missing on disk"
            expected_sha = item["sha256"]
            actual_sha = compute_file_sha256(disk_file)
            assert actual_sha == expected_sha, (
                f"Hash mismatch on {item['path']}: expected {expected_sha}, got {actual_sha}"
            )


def test_p209_safety_and_custody_guarantees() -> None:
    """Test that all packages are strictly held under human custody with zero leaks."""
    with INDEX_PATH.open("r", encoding="utf-8") as f:
        index_data = json.load(f)

    safety = index_data.get("safety_guarantee", {})
    assert safety.get("autonomous_emails_sent") == 0
    assert safety.get("external_api_calls") == 0
    assert safety.get("human_submission_status") == "pending_human_submission"
    assert safety.get("corresponding_author") == "Alexandre Zanata"

    email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

    for curator in CURATORS:
        pkg_data = index_data["curator_packages"][curator]
        assert pkg_data.get("status") == "pending_human_submission"

        for letter_name in ["submission-letter.md", "submission-letter.txt"]:
            letter_path = PACKAGES_DIR / curator / letter_name
            text = letter_path.read_text(encoding="utf-8")
            emails = email_pattern.findall(text)
            assert not emails, f"Found private third-party email in {letter_path}: {emails}"
