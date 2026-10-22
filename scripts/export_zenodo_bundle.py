"""Zenodo / OSF Open Research Data Bundle Exporter (P159).

Packages all raw benchmark datasets, configurations, research dossiers,
formal Lean 4 modules, execution scripts, and environment metadata into a
self-contained, verifiable bundle with cryptographic SHA-256 checksums
ready for long-term open science archive deposit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def compute_file_sha256(path: Path | str, chunk_size: int = 65536) -> str:
    """Compute the SHA-256 hex digest of a file in streaming chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def collect_bundle_files(repo_root: Path) -> list[tuple[Path, str]]:
    """Identify and select all eligible research artifacts for open science archiving.

    Returns a list of tuples (source_path, target_relative_path).
    """
    entries: list[tuple[Path, str]] = []
    root = repo_root.resolve()

    # Core metadata & container recipe
    for fname in ["Dockerfile", ".dockerignore", "Makefile", "pyproject.toml", "README.md", "LICENSE"]:
        src = root / fname
        if src.is_file():
            entries.append((src, fname))

    # Research dossiers & formal hypothesis documentation
    for doc_path in root.glob("docs/research/*.md"):
        if doc_path.is_file():
            rel = doc_path.relative_to(root).as_posix()
            entries.append((doc_path, rel))

    for core_doc in ["docs/HYPOTHESIS.md", "docs/SYSTEMS.md", "docs/ROADMAP.md", "docs/COMMITS.md"]:
        src = root / core_doc
        if src.is_file():
            entries.append((src, core_doc))

    # Phase specifications for empirical evaluation
    for phase_path in root.glob("docs/phases/P15*.md"):
        if phase_path.is_file():
            rel = phase_path.relative_to(root).as_posix()
            entries.append((phase_path, rel))

    # Benchmarking and reproduction scripts
    for bench_path in root.glob("benchmarks/*.py"):
        if bench_path.is_file() and not bench_path.name.startswith("."):
            rel = bench_path.relative_to(root).as_posix()
            entries.append((bench_path, rel))

    # Reproduction scripts in scripts/
    for script_path in root.glob("scripts/*.py"):
        if script_path.is_file() and not script_path.name.startswith("."):
            rel = script_path.relative_to(root).as_posix()
            entries.append((script_path, rel))

    # Experiments: configs, runners, and result summaries for P153-P169 and the
    # validated-discovery program (P161-P170 evidence stays inside experiments/)
    for exp_pattern in ("experiments/p15*", "experiments/p16*"):
        for exp_file in root.glob(exp_pattern):
            if exp_file.is_file():
                rel = exp_file.relative_to(root).as_posix()
                entries.append((exp_file, rel))
            elif exp_file.is_dir() and not exp_file.name.startswith("."):
                # Include json / csv / log result files inside experiment run directories
                for sub_file in exp_file.rglob("*"):
                    if sub_file.is_file() and sub_file.suffix in {".json", ".csv", ".txt", ".log", ".md"}:
                        rel = sub_file.relative_to(root).as_posix()
                        entries.append((sub_file, rel))

    # Audited publication manuscript and data tables (P160, P170)
    for doc_rel in [
        "docs/paper/main.tex",
        "docs/paper/main.pdf",
        "docs/paper/references.bib",
        "docs/paper/table_ablations.tex",
        "docs/paper/table_h1_verdict.tex",
        "docs/paper/table_pareto.tex",
        "docs/paper/table_wilcoxon.tex",
        "docs/research/lean-fidelity-reviews.json",
        "docs/research/targets/open_targets.json",
    ]:
        src = root / doc_rel
        if src.is_file():
            entries.append((src, doc_rel))

    # Project source code (engine, baselines, verifiers, statistical evaluation)
    for src_file in root.glob("src/**/*.py"):
        if src_file.is_file() and "__pycache__" not in src_file.parts:
            entries.append((src_file, src_file.relative_to(root).as_posix()))

    # Standalone external-validation certificate (P167): must be verifiable
    # without installing the package, so it ships as an explicit artifact.
    for standalone_rel in [
        "scripts/verify_certificate_standalone.py",
        "dist/external-validation/sample_certificate.json",
    ]:
        src = root / standalone_rel
        if src.is_file():
            entries.append((src, standalone_rel))

    # Formal Lean 4 sources (excluding build artifacts and mathlib lake cache)
    lean_dir = root / "lean_proofs"
    if lean_dir.is_dir():
        for l_file in lean_dir.rglob("*.lean"):
            rel = l_file.relative_to(root).as_posix()
            if ".lake" not in rel and "build" not in rel:
                entries.append((l_file, rel))
        lake_file = lean_dir / "lakefile.lean"
        if lake_file.is_file():
            entries.append((lake_file, "lean_proofs/lakefile.lean"))

    # De-duplicate while preserving order
    seen: set[str] = set()
    deduped: list[tuple[Path, str]] = []
    for src, rel in entries:
        if rel not in seen and src.exists():
            seen.add(rel)
            deduped.append((src, rel))

    return deduped


def generate_bundle(
    output_dir: Path | str,
    create_tar: bool = True,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Assemble the Zenodo / OSF open research bundle with full cryptographic manifests."""
    t0 = time.perf_counter()
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[1]
    root = repo_root.resolve()
    out_dir = Path(output_dir).resolve()
    content_dir = out_dir / "evobyte-research-bundle"

    if content_dir.exists():
        shutil.rmtree(content_dir)
    content_dir.mkdir(parents=True, exist_ok=True)

    items = collect_bundle_files(root)
    file_manifest: dict[str, dict[str, Any]] = {}
    checksum_lines: list[str] = []

    for src, rel_target in items:
        dst = content_dir / rel_target
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

        sha = compute_file_sha256(dst)
        size = dst.stat().st_size
        file_manifest[rel_target] = {
            "path": rel_target,
            "sha256": sha,
            "size_bytes": size,
        }
        checksum_lines.append(f"{sha}  {rel_target}\n")

    # Sort checksums by file path for canonical determinism
    checksum_lines.sort(key=lambda line: line.split("  ")[1])

    # Git metadata
    git_commit = "unknown"
    git_status = "clean"
    try:
        from evobyte.provenance import get_git_commit, get_git_status

        git_commit = get_git_commit()
        git_status = get_git_status()
    except Exception:
        pass

    metadata: dict[str, Any] = {
        "title": "EvoByte: Deterministic Verification and Evolutionary Bytecode Synthesis Benchmark Archive",
        "description": (
            "Complete empirical evaluation datasets, wall-clock benchmark measurements, "
            "ablation studies, generalization audits, statistical tests, and formal Lean 4 certificates "
            "supporting the validation of Hypothesis H1."
        ),
        "license": "MIT",
        "date_created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": git_commit,
        "git_clean": git_status == "",
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python_version": sys.version.split()[0],
        },
        "total_files": len(file_manifest),
        "total_bytes": sum(m["size_bytes"] for m in file_manifest.values()),
    }

    # Write metadata
    meta_path = content_dir / "bundle_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, sort_keys=True)
    meta_sha = compute_file_sha256(meta_path)
    file_manifest["bundle_metadata.json"] = {
        "path": "bundle_metadata.json",
        "sha256": meta_sha,
        "size_bytes": meta_path.stat().st_size,
    }
    checksum_lines.append(f"{meta_sha}  bundle_metadata.json\n")
    checksum_lines.sort(key=lambda line: line.split("  ")[1])

    # Write manifests
    manifest_path = content_dir / "manifest-sha256.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(file_manifest, f, indent=2, sort_keys=True)

    checksum_path = content_dir / "checksums.sha256"
    with open(checksum_path, "w", encoding="utf-8") as f:
        f.writelines(checksum_lines)

    tar_path: Path | None = None
    if create_tar:
        tar_path = out_dir / "evobyte-zenodo-bundle.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(content_dir, arcname="evobyte-zenodo-bundle")

    elapsed = time.perf_counter() - t0
    bundle_summary: dict[str, Any] = {
        "status": "SUCCESS",
        "output_dir": str(content_dir),
        "tarball_path": str(tar_path) if tar_path else None,
        "total_files": len(file_manifest),
        "total_bytes": sum(m["size_bytes"] for m in file_manifest.values()),
        "manifest_path": str(manifest_path),
        "checksums_path": str(checksum_path),
        "metadata_path": str(meta_path),
        "git_commit": git_commit,
        "elapsed_sec": elapsed,
    }
    return bundle_summary


def verify_zenodo_bundle_integrity(bundle_dir: Path | str) -> tuple[bool, list[str]]:
    """Audit every file in the bundle against manifest-sha256.json and checksums.sha256.

    Returns (is_sound, findings).
    """
    findings: list[str] = []
    b_dir = Path(bundle_dir).resolve()

    manifest_file = b_dir / "manifest-sha256.json"
    checksum_file = b_dir / "checksums.sha256"

    if not manifest_file.is_file():
        findings.append(f"MISSING_MANIFEST: {manifest_file} not found")
        return False, findings

    if not checksum_file.is_file():
        findings.append(f"MISSING_CHECKSUMS: {checksum_file} not found")
        return False, findings

    with open(manifest_file, encoding="utf-8") as f:
        manifest: dict[str, dict[str, Any]] = json.load(f)

    if not manifest or len(manifest) < 5:
        findings.append(f"INSUFFICIENT_FILES: bundle manifest only has {len(manifest)} files")

    # Verify every file against manifest
    for rel_path, meta in manifest.items():
        file_path = b_dir / rel_path
        if not file_path.is_file():
            findings.append(f"MISSING_FILE: file declared in manifest does not exist: {rel_path}")
            continue

        actual_sha = compute_file_sha256(file_path)
        expected_sha = meta.get("sha256")
        if actual_sha != expected_sha:
            findings.append(
                f"CHECKSUM_MISMATCH: {rel_path} expected {expected_sha} but got {actual_sha}"
            )

        actual_size = file_path.stat().st_size
        expected_size = meta.get("size_bytes")
        if actual_size != expected_size:
            findings.append(
                f"SIZE_MISMATCH: {rel_path} expected {expected_size} bytes but got {actual_size}"
            )

    # Cross-check checksums.sha256
    with open(checksum_file, encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            findings.append(f"MALFORMED_CHECKSUM_LINE: {line}")
            continue
        exp_sha, rel_name = parts
        target_path = b_dir / rel_name
        if not target_path.is_file():
            findings.append(f"MISSING_CHECKSUM_FILE: {rel_name} listed in checksums.sha256 not found")
            continue
        actual_sha = compute_file_sha256(target_path)
        if actual_sha != exp_sha:
            findings.append(f"CHECKSUMS_FILE_MISMATCH: {rel_name} hash mismatch in checksums.sha256")

    is_sound = len(findings) == 0
    return is_sound, findings


def main() -> int:
    """CLI entrypoint for Zenodo bundle export and verification."""
    parser = argparse.ArgumentParser(
        description="Export and verify EvoByte open research bundle for Zenodo / OSF."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="dist/zenodo-bundle",
        help="Target output directory for the bundle (default: dist/zenodo-bundle)",
    )
    parser.add_argument(
        "--no-tar",
        action="store_true",
        help="Skip creation of compressed tarball archive",
    )
    parser.add_argument(
        "--verify",
        type=str,
        default=None,
        help="Path to existing bundle directory to verify integrity",
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=None,
        help="Path to repository root (defaults to detected repo root)",
    )

    args = parser.parse_args()

    if args.verify:
        v_path = Path(args.verify)
        print(f"Auditing Zenodo bundle integrity at: {v_path}")
        sound, findings = verify_zenodo_bundle_integrity(v_path)
        if sound:
            print("BUNDLE INTEGRITY VERIFIED: 100% SHA-256 match, zero findings.")
            return 0
        else:
            print(f"BUNDLE CORRUPTED OR INCOMPLETE ({len(findings)} findings):")
            for f in findings:
                print(f"  - {f}")
            return 1

    root = Path(args.repo_root) if args.repo_root else None
    out_dir = Path(args.output_dir)
    print(f"Generating Zenodo open research bundle at: {out_dir}")
    summary = generate_bundle(
        output_dir=out_dir,
        create_tar=not args.no_tar,
        repo_root=root,
    )
    print(
        f"Bundle export complete: {summary['total_files']} files, "
        f"{summary['total_bytes'] / (1024 * 1024):.2f} MB in {summary['elapsed_sec']:.2f}s."
    )
    if summary["tarball_path"]:
        print(f"Archive generated at: {summary['tarball_path']}")

    # Self-verify generated content directory
    sound, findings = verify_zenodo_bundle_integrity(summary["output_dir"])
    if not sound:
        print(f"Self-verification failed: {findings}")
        return 1
    print("Bundle self-verification passed: all SHA-256 checksums match.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
