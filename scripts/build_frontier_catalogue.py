#!/usr/bin/env python3
"""Build and verify Frontier Target Catalogue v2.

Deterministic generation of:
- docs/research/targets/ljcr_pool_v2.json
- docs/research/targets/frontier_sources_v2.json
- docs/research/targets/certificates/*.json
- docs/research/targets/frontier_targets_v2.json

Usage:
    python3 scripts/build_frontier_catalogue.py          # rebuilds files
    python3 scripts/build_frontier_catalogue.py --check  # verifies committed files match
"""

from __future__ import annotations

import argparse
import ast
import itertools
import json
import math
from pathlib import Path
import random
import re
import subprocess
import sys
import time
from typing import Any

from evobyte.frontier_catalogue import (
    load_frontier_catalogue,
    verify_cap_set,
    verify_covering_design,
    verify_weak_schur_partition,
)
from evobyte.target_catalogue import verify_schur_partition

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw" / "frontier"
TARGETS_DIR = REPO_ROOT / "docs" / "research" / "targets"
CERTS_DIR = TARGETS_DIR / "certificates"

SOURCES_META: dict[str, dict[str, Any]] = {
    "ljcr-coverdata-459bcaf": {
        "source_id": "ljcr-coverdata-459bcaf",
        "url": "https://raw.githubusercontent.com/dmgordo/LJCR/459bcaf247bd8d34610d946b0465864f7d4dfa37/coverings/coverdata.json",
        "sha256": "0984bb8b4c89fe07268569b9814794e3c8852302d075f0794140f202e83d7fef",
        "accessed_at": "2026-10-22T18:07:43-04:00",
        "pinned_commit": "459bcaf247bd8d34610d946b0465864f7d4dfa37",
        "live_site_status": "unreachable",
        "notes": "Gordon LJCR covering table JSON snapshot. Live sites ljcr.dmgordon.org and dmgordon.org/cover are unreachable (DNS failure / 404).",
    },
    "oeis-A118771": {
        "source_id": "oeis-A118771",
        "url": "https://oeis.org/search?q=id:A118771&fmt=text",
        "sha256": "0ab6b7a4cf9a10f53c1b4a2b5aabb1e100bb0eccba513312d843bb998c83d606",
        "accessed_at": "2026-10-22T18:08:07-04:00",
        "pinned_commit": None,
        "notes": "OEIS A118771: Weak Schur numbers (convention: smallest s without sum-free partition).",
    },
    "oeis-A072842": {
        "source_id": "oeis-A072842",
        "url": "https://oeis.org/search?q=id:A072842&fmt=text",
        "sha256": "703ead14a0aa95a0759831b50dc794af0894587d4bf991cf21a5a7e91f840273",
        "accessed_at": "2026-10-22T18:09:30-04:00",
        "pinned_commit": None,
        "notes": "OEIS A072842: Weak Schur numbers (convention: largest m with valid partition). Cites Rowley (2025) WS(5)>=207 and Rodrigo (2026) WS(6)>=650.",
    },
    "oeis-A030126": {
        "source_id": "oeis-A030126",
        "url": "https://oeis.org/search?q=id:A030126&fmt=text",
        "sha256": "3351d13b3f0ca477c30ffd407cb0ccb50afbd4df8dbe730b3a214a7e44e47f44",
        "accessed_at": "2026-10-22T18:08:07-04:00",
        "pinned_commit": None,
        "notes": "OEIS A030126: Schur numbers (version 1, smallest s without partition). Cites Heule (2017) S(5)=160 exact partition.",
    },
    "oeis-A090245": {
        "source_id": "oeis-A090245",
        "url": "https://oeis.org/search?q=id:A090245&fmt=text",
        "sha256": "33faf08316d3fb4f493996908878cd549d54e859e1bfa479e518f349dfd7e940",
        "accessed_at": "2026-10-22T18:08:07-04:00",
        "pinned_commit": None,
        "notes": "OEIS A090245: Maximum cap set size in F3^n. Cites Romera-Paredes et al. (2024) FunSearch cap set.",
    },
    "zenodo-20633634": {
        "source_id": "zenodo-20633634",
        "url": "https://doi.org/10.5281/zenodo.20633634",
        "sha256": "6d39fe1180e7e9d239f90940cc13ffead95b60f7f563a5bda6b435da9e49f4ce",
        "accessed_at": "2026-10-22T18:10:20-04:00",
        "pinned_commit": None,
        "notes": "Sebastián E. Rodrigo (2026): A new lower bound for the sixth weak Schur number: WS(6) >= 650 with witness digits archive.",
    },
    "fredricksen-sweet-2000": {
        "source_id": "fredricksen-sweet-2000",
        "url": "https://www.combinatorics.org/ojs/index.php/eljc/article/download/v7i1r32/pdf/",
        "sha256": "ae8541c564efd65785a0e1d2c778108d58fec4c060707d7c277dd7f3eecad259",
        "accessed_at": "2026-10-22T18:11:29-04:00",
        "pinned_commit": None,
        "notes": "Harold Fredricksen and Melvin M. Sweet (2000): Symmetric Sum-Free Partitions and Lower Bounds for Schur Numbers. Shows S(6)>=536 and S(7)>=1680.",
    },
    "funsearch-nature-2024": {
        "source_id": "funsearch-nature-2024",
        "url": "https://raw.githubusercontent.com/google-deepmind/funsearch/main/cap_set/n8_size512.txt",
        "sha256": "8d6df45c3039b6a7ee1aae7216b100c3f4c075179dc6471f4f51b968a26d8905",
        "accessed_at": "2026-10-22T18:12:09-04:00",
        "pinned_commit": None,
        "notes": "Romera-Paredes et al. (Nature 2024): Mathematical discoveries from program search with LLMs. Cap set in F3^8 of size 512.",
    },
    "edel-caps-tables": {
        "source_id": "edel-caps-tables",
        "url": "http://www.yvesedel.de/Matritzen/CAPs/CAPMatIndex.html",
        "sha256": "8aa5a2837a51d261c7b030e500c2c99e396d9ce7a653ecce8bc9badf6c1e2817",
        "accessed_at": "2026-10-22T18:14:38-04:00",
        "pinned_commit": None,
        "notes": "Yves Edel: Generator matrices for caps and table of lower bounds.",
    },
    "edel-248-7-3": {
        "source_id": "edel-248-7-3",
        "url": "http://www.yvesedel.de/Matritzen/CAPs/Matrizen/(248,7,3).html",
        "sha256": "056e5f40945cc26883034cab3037e552fe73f0dccb8d2626407dd6a623d1910a",
        "accessed_at": "2026-10-22T18:17:50-04:00",
        "pinned_commit": None,
        "notes": "Yves Edel: Generator matrix of 248-cap in PG(7,3) containing Calderbank-Fishburn 236-cap in AG(7,3).",
    },
}


def build_ljcr_pool(coverdata_path: Path) -> dict[str, Any]:
    """Filter LJCR entries matching frozen criteria and return pool dictionary."""
    with coverdata_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    pool_entries: dict[str, Any] = {}
    for name, entry in data.items():
        m = re.match(r"C\((\d+),(\d+),(\d+)\)", name)
        if not m:
            continue
        v, k, t = map(int, m.groups())
        size = entry["size"]
        low_bd = entry["low_bd"]
        if size > low_bd and 2 <= t <= 6 and math.comb(v, t) <= 10_000_000 and size <= 2000:
            imp0 = entry["imps"][0] if entry.get("imps") else ["", "", "", ""]
            n_2020 = sum(
                1
                for imp in entry.get("imps", [])
                if imp[3] and imp[3][:4].isdigit() and int(imp[3][:4]) >= 2020
            )
            pool_entries[name] = {
                "name": name,
                "v": v,
                "k": k,
                "t": t,
                "size": size,
                "low_bd": low_bd,
                "last_improvement_date": imp0[3][:10] if imp0[3] else None,
                "last_improvement_author": imp0[1] if len(imp0) > 1 else "",
                "last_improvement_method": imp0[2] if len(imp0) > 2 else "",
                "n_improvements_since_2020": n_2020,
            }

    sorted_entries = dict(sorted(pool_entries.items(), key=lambda kv: kv[0]))
    return {
        "pool_size": len(sorted_entries),
        "entries": sorted_entries,
    }


def select_covering_targets(
    pool_dict: dict[str, Any],
) -> tuple[list[str], list[str], list[str]]:
    """Execute the frozen deterministic selection rule on LJCR pool entries.

    Returns:
        (stale_construction_20, active_frontier_10, random_control_10)
    """
    entries = pool_dict["entries"] if "entries" in pool_dict else pool_dict

    keywords = [
        "multiple of",
        "construction",
        "extraction",
        "remainder",
        "combin",
        "jcd article",
        "greedy",
        "wang",
        "from (",
    ]

    scored = []
    for name, entry in entries.items():
        v, k, t = entry["v"], entry["k"], entry["t"]
        text = (entry["last_improvement_method"] + " " + entry["last_improvement_author"]).lower()
        construction = 1 if any(kw in text for kw in keywords) else 0
        date_str = entry["last_improvement_date"] or ""
        ano = int(date_str[:4]) if date_str[:4].isdigit() else 2026
        score = (
            1.0 * construction
            + 0.02 * min(2026 - ano, 25)
            + 0.5 * (entry["size"] - entry["low_bd"]) / entry["size"]
        )
        scored.append((-score, v, k, t, name))

    scored.sort()
    stale: list[str] = []
    t_counts: dict[int, int] = {}
    for item in scored:
        t = item[3]
        if t_counts.get(t, 0) < 5:
            stale.append(item[4])
            t_counts[t] = t_counts.get(t, 0) + 1
            if len(stale) == 20:
                break

    stale_set = set(stale)
    active_cand = []
    for name, entry in entries.items():
        if name in stale_set:
            continue
        if entry["n_improvements_since_2020"] >= 2:
            active_cand.append((-entry["n_improvements_since_2020"], name))
    active_cand.sort()
    active = [name for _, name in active_cand[:10]]
    active_set = set(active)

    remaining = sorted(
        [name for name in entries if name not in stale_set and name not in active_set]
    )
    rand_ctrl = random.Random(171).sample(remaining, 10)

    return stale, active, rand_ctrl


def build_certificates(certs_dir: Path, raw_dir: Path) -> dict[str, str]:
    """Construct, verify, and write all 12 published/calibration certificates."""
    certs_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}

    # 1. Fano plane C(7,3,2)
    fano = [[1, 2, 3], [1, 4, 5], [1, 6, 7], [2, 4, 6], [2, 5, 7], [3, 4, 7], [3, 5, 6]]
    ok, msg = verify_covering_design(fano, 7, 3, 2)
    assert ok, f"Fano verification failed: {msg}"
    p = certs_dir / "covering_C_7_3_2.json"
    p.write_text(json.dumps({"target_id": "covering_C_7_3_2", "blocks": fano}, indent=2) + "\n")
    paths["covering_C_7_3_2"] = f"docs/research/targets/certificates/{p.name}"

    # 2. AG(2,3) C(9,3,2)
    ag23 = []
    for a in (0, 1, 2):
        for b in (0, 1, 2):
            if a == 0 and b == 0:
                continue
            if a == 0 and b != 1:
                continue
            if a == 2:
                continue
            for c in (0, 1, 2):
                line = []
                for x in (0, 1, 2):
                    for y in (0, 1, 2):
                        if (a * x + b * y) % 3 == c:
                            line.append(1 + 3 * x + y)
                ag23.append(sorted(line))
    ok, msg = verify_covering_design(ag23, 9, 3, 2)
    assert ok, f"AG(2,3) verification failed: {msg}"
    p = certs_dir / "covering_C_9_3_2.json"
    p.write_text(json.dumps({"target_id": "covering_C_9_3_2", "blocks": ag23}, indent=2) + "\n")
    paths["covering_C_9_3_2"] = f"docs/research/targets/certificates/{p.name}"

    # 3. S(3,4,8) C(8,4,3)
    s348 = []
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                if a == 0 and b == 0 and c == 0:
                    continue
                for d in (0, 1):
                    plane = []
                    for x in (0, 1):
                        for y in (0, 1):
                            for z in (0, 1):
                                if (a * x + b * y + c * z) % 2 == d:
                                    plane.append(1 + 4 * x + 2 * y + z)
                    s348.append(sorted(plane))
    ok, msg = verify_covering_design(s348, 8, 4, 3)
    assert ok, f"S(3,4,8) verification failed: {msg}"
    p = certs_dir / "covering_C_8_4_3.json"
    p.write_text(json.dumps({"target_id": "covering_C_8_4_3", "blocks": s348}, indent=2) + "\n")
    paths["covering_C_8_4_3"] = f"docs/research/targets/certificates/{p.name}"

    # 4. weak_schur_5 (Rowley 207)
    ws5_witness = raw_dir / "ws6_records" / "ws6_records_20260610" / "witnesses" / "ws5_207_rowley_verified.digits"
    with ws5_witness.open("r", encoding="utf-8") as f:
        ws5_coloring = [int(c) for c in f.read().strip() if c.isdigit()]
    assert len(ws5_coloring) == 207
    ok, msg = verify_weak_schur_partition(ws5_coloring, 5)
    assert ok, f"WS(5) verification failed: {msg}"
    p = certs_dir / "weak_schur_5.json"
    p.write_text(json.dumps({"target_id": "weak_schur_5", "coloring": ws5_coloring}, indent=2) + "\n")
    paths["weak_schur_5"] = f"docs/research/targets/certificates/{p.name}"

    # 5. weak_schur_6 (Rodrigo 650)
    ws6_witness = raw_dir / "ws6_records" / "ws6_records_20260610" / "witnesses" / "ws6_650_WITNESS.digits"
    with ws6_witness.open("r", encoding="utf-8") as f:
        ws6_coloring = [int(c) for c in f.read().strip() if c.isdigit()]
    assert len(ws6_coloring) == 650
    ok, msg = verify_weak_schur_partition(ws6_coloring, 6)
    assert ok, f"WS(6) verification failed: {msg}"
    p = certs_dir / "weak_schur_6.json"
    p.write_text(json.dumps({"target_id": "weak_schur_6", "coloring": ws6_coloring}, indent=2) + "\n")
    paths["weak_schur_6"] = f"docs/research/targets/certificates/{p.name}"

    # 6. schur_5 (Marijn Heule 160)
    A = {1, 6, 10, 18, 21, 23, 26, 30, 34, 38, 43, 45, 50, 54, 65, 74, 87, 96, 107, 111, 116, 118, 123, 127, 131, 135, 138, 140, 143, 151, 155, 160}
    B = {2, 3, 8, 14, 19, 20, 24, 25, 36, 46, 47, 51, 62, 73, 88, 99, 110, 114, 115, 125, 136, 137, 141, 142, 147, 153, 158, 159}
    C = {4, 5, 15, 16, 22, 28, 29, 39, 40, 41, 42, 48, 49, 59, 102, 112, 113, 119, 120, 121, 122, 132, 133, 139, 145, 146, 156, 157}
    D = {7, 9, 11, 12, 13, 17, 27, 31, 32, 33, 35, 37, 53, 56, 57, 61, 79, 82, 100, 104, 105, 108, 124, 126, 128, 129, 130, 134, 144, 148, 149, 150, 152, 154}
    E = {44, 52, 55, 58, 60, 63, 64, 66, 67, 68, 69, 70, 71, 72, 75, 76, 77, 78, 80, 81, 83, 84, 85, 86, 89, 90, 91, 92, 93, 94, 95, 97, 98, 101, 103, 106, 109, 117}
    s5_coloring = [0] * 160
    for idx, s in enumerate([A, B, C, D, E], 1):
        for x in s:
            s5_coloring[x - 1] = idx
    ok, msg = verify_schur_partition(s5_coloring, 5)
    assert ok, f"S(5) verification failed: {msg}"
    p = certs_dir / "schur_5.json"
    p.write_text(json.dumps({"target_id": "schur_5", "coloring": s5_coloring}, indent=2) + "\n")
    paths["schur_5"] = f"docs/research/targets/certificates/{p.name}"

    # 7. schur_6 (Fredricksen & Sweet 536)
    pdf_path = raw_dir / "fredricksen_sweet_2000.pdf"
    pdf_text = subprocess.check_output(["pdftotext", str(pdf_path), "-"]).decode("utf-8")
    p_start = pdf_text.find("Partition of 536 into 6 symmetric sumfree sets:")
    p_end = pdf_text.find("Partition of 1680 into 7 symmetric sumfree sets:")
    chunk = pdf_text[p_start:p_end]
    sets_6: dict[int, list[int]] = {}
    cur: int | None = None
    for line in chunk.splitlines():
        line = line.strip()
        m = re.match(r"Set\s+(\d+):", line)
        if m:
            cur = int(m.group(1))
            sets_6[cur] = []
        elif cur and line and not line.startswith("the electronic") and not line.startswith("\x0c"):
            if line.startswith("(") or line.startswith("We also"):
                cur = None
                continue
            sets_6[cur].extend(int(x) for x in line.split() if x.isdigit())
    full_6 = {k: set(v) for k, v in sets_6.items()}
    for k, v in sets_6.items():
        for x in v:
            if x != 179 and x != 358:
                full_6[k].add(537 - x)
    s6_coloring = [0] * 536
    for k, s in full_6.items():
        for x in s:
            s6_coloring[x - 1] = k
    ok, msg = verify_schur_partition(s6_coloring, 6)
    assert ok, f"S(6) verification failed: {msg}"
    p = certs_dir / "schur_6.json"
    p.write_text(json.dumps({"target_id": "schur_6", "coloring": s6_coloring}, indent=2) + "\n")
    paths["schur_6"] = f"docs/research/targets/certificates/{p.name}"

    # 8. schur_7 (Fredricksen & Sweet 1680)
    pages = pdf_text.split("\x0c")
    p7_lines = [l.strip() for l in pages[6].splitlines() if l.strip()][1:-1]
    p8_lines = [l.strip() for l in pages[7].splitlines() if l.strip()][2:]
    sets_7: dict[int, list[int]] = {}
    cur = None
    for line in p7_lines + p8_lines:
        m = re.match(r"Set\s+(\d+):", line)
        if m:
            cur = int(m.group(1))
            sets_7[cur] = []
        elif cur:
            if line.startswith("(") or line.startswith("We also"):
                cur = None
                continue
            sets_7[cur].extend(int(x) for x in line.split() if x.isdigit())
    full_7 = {k: set(v) for k, v in sets_7.items()}
    for k, v in sets_7.items():
        for x in v:
            full_7[k].add(1681 - x)
    s7_coloring = [0] * 1680
    for k, s in full_7.items():
        for x in s:
            s7_coloring[x - 1] = k
    ok, msg = verify_schur_partition(s7_coloring, 7)
    assert ok, f"S(7) verification failed: {msg}"
    p = certs_dir / "schur_7.json"
    p.write_text(json.dumps({"target_id": "schur_7", "coloring": s7_coloring}, indent=2) + "\n")
    paths["schur_7"] = f"docs/research/targets/certificates/{p.name}"

    # 9. cap_set_3 (9-cap)
    c3_pts = [
        [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1],
        [1, 0, 0], [1, 0, 1], [1, 1, 2], [1, 2, 2], [2, 1, 2],
    ]
    ok, msg = verify_cap_set(c3_pts, 3)
    assert ok, f"Cap(3) verification failed: {msg}"
    p = certs_dir / "cap_set_3.json"
    p.write_text(json.dumps({"target_id": "cap_set_3", "points": c3_pts}, indent=2) + "\n")
    paths["cap_set_3"] = f"docs/research/targets/certificates/{p.name}"

    # 10. cap_set_7 (Calderbank-Fishburn 236-cap)
    edel_html = (raw_dir / "edel_248_7_3.html").read_text(encoding="utf-8")
    matrix_lines = [
        line.strip().replace("<BR>", "")
        for line in edel_html.splitlines()
        if line.strip().startswith(("0", "1", "2"))
    ]
    last_row = matrix_lines[7]
    c7_pts = []
    for col in range(len(last_row)):
        if last_row[col] == "1":
            c7_pts.append([int(matrix_lines[r][col]) for r in range(7)])
    assert len(c7_pts) == 236
    ok, msg = verify_cap_set(c7_pts, 7)
    assert ok, f"Cap(7) verification failed: {msg}"
    p = certs_dir / "cap_set_7.json"
    p.write_text(json.dumps({"target_id": "cap_set_7", "points": c7_pts}, indent=2) + "\n")
    paths["cap_set_7"] = f"docs/research/targets/certificates/{p.name}"

    # 11. cap_set_8 (FunSearch 512-cap)
    fn8 = raw_dir / "funsearch_n8_size512.txt"
    c8_pts = [ast.literal_eval(line.strip()) for line in fn8.open("r", encoding="utf-8")]
    assert len(c8_pts) == 512
    ok, msg = verify_cap_set(c8_pts, 8)
    assert ok, f"Cap(8) verification failed: {msg}"
    p = certs_dir / "cap_set_8.json"
    p.write_text(json.dumps({"target_id": "cap_set_8", "points": c8_pts}, indent=2) + "\n")
    paths["cap_set_8"] = f"docs/research/targets/certificates/{p.name}"

    # 12. cap_set_9 (FunSearch / Edel 1082-cap)
    def priority(el: tuple[int, ...], n: int) -> float:
        weight = sum(x * x for x in el) % 3
        a = n // 3
        b = n - n // 3
        s_1 = sum(x * x for x in el[:b]) % 3
        s_3 = (2 * sum(x * x for x in el[:a])) % 3
        s_4 = sum(x * y for x, y in zip(el[:a], el[a:b])) % 3
        s_5 = sum(1 for x in el[:a] if x == el[-1]) % 3
        return -27 * s_1 + 9 * weight + 27 * s_3 + 9 * s_4 + s_5

    all_vecs = list(itertools.product((0, 1, 2), repeat=9))
    priorities = [priority(v, 9) for v in all_vecs]
    order = sorted(range(len(all_vecs)), key=lambda i: -priorities[i])
    c9_pts = []
    seen = set()
    for idx in order:
        v = all_vecs[idx]
        if not any(tuple((-(x + y)) % 3 for x, y in zip(v, p)) in seen for p in c9_pts):
            c9_pts.append(list(v))
            seen.add(v)
    assert len(c9_pts) == 1082
    ok, msg = verify_cap_set(c9_pts, 9)
    assert ok, f"Cap(9) verification failed: {msg}"
    p = certs_dir / "cap_set_9.json"
    p.write_text(json.dumps({"target_id": "cap_set_9", "points": c9_pts}, indent=2) + "\n")
    paths["cap_set_9"] = f"docs/research/targets/certificates/{p.name}"

    return paths


def measure_target_runtime(target: dict[str, Any]) -> float:
    """Measure the verification runtime in seconds using standard seed 171."""
    family = target["family"]
    rng = random.Random(171)

    if family == "covering_design":
        v = target["params"]["v"]
        k = target["params"]["k"]
        t = target["params"]["t"]
        size = target["best_known_value"]
        blocks = [rng.sample(range(1, v + 1), k) for _ in range(size)]
        t0 = time.perf_counter()
        verify_covering_design(blocks, v, k, t)
        return round(time.perf_counter() - t0, 4)

    elif family == "weak_schur":
        k = target["params"]["k"]
        n = target["best_known_value"]
        coloring = [rng.randint(1, k) for _ in range(n)]
        t0 = time.perf_counter()
        verify_weak_schur_partition(coloring, k)
        return round(time.perf_counter() - t0, 6)

    elif family == "schur":
        k = target["params"]["k"]
        n = target["best_known_value"]
        coloring = [rng.randint(1, k) for _ in range(n)]
        t0 = time.perf_counter()
        verify_schur_partition(coloring, k)
        return round(time.perf_counter() - t0, 6)

    elif family == "cap_set":
        n = target["params"]["n"]
        size = target["best_known_value"]
        pts = [tuple(rng.randint(0, 2) for _ in range(n)) for _ in range(size)]
        t0 = time.perf_counter()
        verify_cap_set(pts, n)
        return round(time.perf_counter() - t0, 6)

    return 0.0


def build_catalogue(retime: bool = False) -> dict[str, Any]:
    """Build the complete Catalogue v2 dictionary with all targets."""
    coverdata_path = RAW_DIR / "coverdata.json"
    pool_dict = build_ljcr_pool(coverdata_path)
    entries = pool_dict["entries"]
    stale, active, rand_ctrl = select_covering_targets(pool_dict)

    # Existing runtimes cache if present
    cached_runtimes: dict[str, float] = {}
    targets_json_path = TARGETS_DIR / "frontier_targets_v2.json"
    if targets_json_path.exists() and not retime:
        try:
            with targets_json_path.open("r", encoding="utf-8") as f:
                old_data = json.load(f)
                for t in old_data.get("targets", []):
                    cached_runtimes[t["target_id"]] = t.get("verifier_runtime_s", 0.0)
        except Exception:
            pass

    targets: list[dict[str, Any]] = []

    # 1. Covering record targets (20 stale, 10 active, 10 random_control)
    covering_groups = [
        ("stale_construction", stale),
        ("active_frontier", active),
        ("random_control", rand_ctrl),
    ]
    for stratum, names in covering_groups:
        for name in names:
            ent = entries[name]
            v, k, t = ent["v"], ent["k"], ent["t"]
            size = ent["size"]
            low_bd = ent["low_bd"]
            tid = f"covering_C_{v}_{k}_{t}"
            t_obj: dict[str, Any] = {
                "target_id": tid,
                "family": "covering_design",
                "params": {"v": v, "k": k, "t": t},
                "objective": "minimize",
                "role": "record",
                "stratum": stratum,
                "best_known_value": size,
                "source_convention": "Number of k-element blocks covering all t-subsets of a v-set in Gordon LJCR repository.",
                "claimed_values": [
                    {
                        "value": size,
                        "source_id": "ljcr-coverdata-459bcaf",
                        "verified_object": False,
                    }
                ],
                "lower_bound": low_bd,
                "proven_optimal": False,
                "last_improvement": ent["last_improvement_date"],
                "last_method": f"{ent['last_improvement_method']} {ent['last_improvement_author']}".strip(),
                "certificate_status": "site_unreachable",
                "certificate_path": None,
                "verifier": "verify_covering_design",
                "verifier_runtime_s": 0.0,
            }
            if tid in cached_runtimes and not retime:
                t_obj["verifier_runtime_s"] = cached_runtimes[tid]
            else:
                t_obj["verifier_runtime_s"] = measure_target_runtime(t_obj)
            targets.append(t_obj)

    # 2. Covering calibration targets (3)
    cov_calib = [
        (
            "covering_C_7_3_2",
            7, 3, 2, 7, 7,
            "1890-01-01",
            "Fano plane PG(2,2)",
            "docs/research/targets/certificates/covering_C_7_3_2.json",
        ),
        (
            "covering_C_9_3_2",
            9, 3, 2, 12, 12,
            "1900-01-01",
            "Affine plane AG(2,3)",
            "docs/research/targets/certificates/covering_C_9_3_2.json",
        ),
        (
            "covering_C_8_4_3",
            8, 4, 3, 14, 14,
            "1938-01-01",
            "Steiner system S(3,4,8)",
            "docs/research/targets/certificates/covering_C_8_4_3.json",
        ),
    ]
    for tid, v, k, t, size, low_bd, last_date, last_meth, cert_path in cov_calib:
        t_obj = {
            "target_id": tid,
            "family": "covering_design",
            "params": {"v": v, "k": k, "t": t},
            "objective": "minimize",
            "role": "calibration",
            "stratum": "calibration",
            "best_known_value": size,
            "source_convention": "Number of k-element blocks covering all t-subsets of a v-set. Proven exact.",
            "claimed_values": [
                {
                    "value": size,
                    "source_id": "ljcr-coverdata-459bcaf",
                    "verified_object": True,
                }
            ],
            "lower_bound": low_bd,
            "proven_optimal": True,
            "last_improvement": last_date,
            "last_method": last_meth,
            "certificate_status": "constructed_calibration",
            "certificate_path": cert_path,
            "verifier": "verify_covering_design",
            "verifier_runtime_s": 0.0,
        }
        if tid in cached_runtimes and not retime:
            t_obj["verifier_runtime_s"] = cached_runtimes[tid]
        else:
            t_obj["verifier_runtime_s"] = measure_target_runtime(t_obj)
        targets.append(t_obj)

    # 3. Weak Schur targets
    ws_targets = [
        (
            "weak_schur_5",
            5,
            207,
            [
                {"value": 207, "source_id": "oeis-A072842", "verified_object": True},
                {"value": 196, "source_id": "oeis-A072842", "verified_object": True},
            ],
            "2025-08-29",
            "Fred Rowley template-based coloring",
            "verified_published_object",
            "docs/research/targets/certificates/weak_schur_5.json",
        ),
        (
            "weak_schur_6",
            6,
            650,
            [
                {"value": 650, "source_id": "zenodo-20633634", "verified_object": True},
                {"value": 646, "source_id": "oeis-A072842", "verified_object": True},
                {"value": 582, "source_id": "oeis-A072842", "verified_object": False},
            ],
            "2026-06-10",
            "Sebastián E. Rodrigo Tabu search with perturbation",
            "verified_published_object",
            "docs/research/targets/certificates/weak_schur_6.json",
        ),
        (
            "weak_schur_7",
            7,
            2146,
            [
                {"value": 2146, "source_id": "oeis-A072842", "verified_object": False},
                {"value": 1740, "source_id": "oeis-A072842", "verified_object": False},
            ],
            "2021-01-01",
            "Fred Rowley template-based partition (Integers 21)",
            "not_obtained",
            None,
        ),
    ]
    for tid, k, bkv, claims, last_date, last_meth, cert_stat, cert_path in ws_targets:
        t_obj = {
            "target_id": tid,
            "family": "weak_schur",
            "params": {"k": k},
            "objective": "maximize",
            "role": "record",
            "stratum": "named_open",
            "best_known_value": bkv,
            "source_convention": f"Largest N such that [1..N] can be partitioned into {k} weakly sum-free subsets (OEIS A072842). Corresponding A118771 value is N+1={bkv + 1}.",
            "claimed_values": claims,
            "lower_bound": bkv,
            "proven_optimal": False,
            "last_improvement": last_date,
            "last_method": last_meth,
            "certificate_status": cert_stat,
            "certificate_path": cert_path,
            "verifier": "verify_weak_schur_partition",
            "verifier_runtime_s": 0.0,
        }
        if tid in cached_runtimes and not retime:
            t_obj["verifier_runtime_s"] = cached_runtimes[tid]
        else:
            t_obj["verifier_runtime_s"] = measure_target_runtime(t_obj)
        targets.append(t_obj)

    # 4. Schur targets
    s_targets = [
        (
            "schur_5",
            5,
            160,
            "calibration",
            "calibration",
            True,
            [{"value": 160, "source_id": "oeis-A030126", "verified_object": True}],
            "2017-11-26",
            "Marijn Heule SAT solver certificate (AAAI 2018)",
            "verified_published_object",
            "docs/research/targets/certificates/schur_5.json",
        ),
        (
            "schur_6",
            6,
            536,
            "record",
            "named_open",
            False,
            [{"value": 536, "source_id": "fredricksen-sweet-2000", "verified_object": True}],
            "2000-01-01",
            "Fredricksen & Sweet symmetric partition (ElJC 7)",
            "verified_published_object",
            "docs/research/targets/certificates/schur_6.json",
        ),
        (
            "schur_7",
            7,
            1680,
            "record",
            "named_open",
            False,
            [{"value": 1680, "source_id": "fredricksen-sweet-2000", "verified_object": True}],
            "2000-01-01",
            "Fredricksen & Sweet symmetric partition (ElJC 7)",
            "verified_published_object",
            "docs/research/targets/certificates/schur_7.json",
        ),
    ]
    for tid, k, bkv, role, stratum, prov_opt, claims, last_date, last_meth, cert_stat, cert_path in s_targets:
        t_obj = {
            "target_id": tid,
            "family": "schur",
            "params": {"k": k},
            "objective": "maximize",
            "role": role,
            "stratum": stratum,
            "best_known_value": bkv,
            "source_convention": f"Largest N such that [1..N] can be partitioned into {k} sum-free subsets (OEIS A030126 version 1 value minus 1).",
            "claimed_values": claims,
            "lower_bound": bkv,
            "proven_optimal": prov_opt,
            "last_improvement": last_date,
            "last_method": last_meth,
            "certificate_status": cert_stat,
            "certificate_path": cert_path,
            "verifier": "verify_schur_partition",
            "verifier_runtime_s": 0.0,
        }
        if tid in cached_runtimes and not retime:
            t_obj["verifier_runtime_s"] = cached_runtimes[tid]
        else:
            t_obj["verifier_runtime_s"] = measure_target_runtime(t_obj)
        targets.append(t_obj)

    # 5. Cap set targets (n=3..10)
    cap_specs = [
        ("cap_set_3", 3, 9, "calibration", "calibration", True, [{"value": 9, "source_id": "oeis-A090245", "verified_object": True}], "1970-01-01", "Exact classical geometry", "constructed_calibration", "docs/research/targets/certificates/cap_set_3.json"),
        ("cap_set_4", 4, 20, "calibration", "calibration", True, [{"value": 20, "source_id": "oeis-A090245", "verified_object": False}], "1970-01-01", "Pellegrino (1970)", "not_obtained", None),
        ("cap_set_5", 5, 45, "calibration", "calibration", True, [{"value": 45, "source_id": "oeis-A090245", "verified_object": False}], "2002-01-01", "Edel, Ferret, Landjev, Storme (2002)", "not_obtained", None),
        ("cap_set_6", 6, 112, "calibration", "calibration", True, [{"value": 112, "source_id": "oeis-A090245", "verified_object": False}], "2008-01-01", "Aaron Potechin (2008)", "not_obtained", None),
        ("cap_set_7", 7, 236, "record", "named_open", False, [{"value": 236, "source_id": "edel-248-7-3", "verified_object": True}], "1994-01-01", "Calderbank & Fishburn (1994) / Edel (2004)", "verified_published_object", "docs/research/targets/certificates/cap_set_7.json"),
        ("cap_set_8", 8, 512, "calibration", "calibration", False, [{"value": 512, "source_id": "funsearch-nature-2024", "verified_object": True}], "2023-12-14", "Romera-Paredes et al., FunSearch (Nature 2024)", "verified_published_object", "docs/research/targets/certificates/cap_set_8.json"),
        ("cap_set_9", 9, 1082, "record", "named_open", False, [{"value": 1082, "source_id": "funsearch-nature-2024", "verified_object": True}], "2004-01-01", "Yves Edel (2004) / FunSearch (2024)", "verified_published_object", "docs/research/targets/certificates/cap_set_9.json"),
        ("cap_set_10", 10, 2240, "record", "named_open", False, [{"value": 2240, "source_id": "edel-caps-tables", "verified_object": False}], "2004-01-01", "Yves Edel product construction (2004)", "not_obtained", None),
    ]
    for tid, n, bkv, role, stratum, prov_opt, claims, last_date, last_meth, cert_stat, cert_path in cap_specs:
        t_obj = {
            "target_id": tid,
            "family": "cap_set",
            "params": {"n": n},
            "objective": "maximize",
            "role": role,
            "stratum": stratum,
            "best_known_value": bkv,
            "source_convention": f"Maximum size of a cap set in F3^{n} (no collinear triples).",
            "claimed_values": claims,
            "lower_bound": bkv,
            "proven_optimal": prov_opt,
            "last_improvement": last_date,
            "last_method": last_meth,
            "certificate_status": cert_stat,
            "certificate_path": cert_path,
            "verifier": "verify_cap_set",
            "verifier_runtime_s": 0.0,
        }
        if tid in cached_runtimes and not retime:
            t_obj["verifier_runtime_s"] = cached_runtimes[tid]
        else:
            t_obj["verifier_runtime_s"] = measure_target_runtime(t_obj)
        targets.append(t_obj)

    return {
        "version": "2.0.0",
        "catalogue_date": "2026-10-22",
        "targets": targets,
    }


def write_all(retime: bool = False) -> None:
    """Build and write all catalogue artifacts."""
    TARGETS_DIR.mkdir(parents=True, exist_ok=True)
    CERTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Sources JSON
    sources_path = TARGETS_DIR / "frontier_sources_v2.json"
    sources_path.write_text(json.dumps(SOURCES_META, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {sources_path} ({len(SOURCES_META)} sources)")

    # 2. LJCR Pool JSON
    coverdata_path = RAW_DIR / "coverdata.json"
    pool_dict = build_ljcr_pool(coverdata_path)
    pool_path = TARGETS_DIR / "ljcr_pool_v2.json"
    pool_path.write_text(json.dumps(pool_dict, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {pool_path} ({pool_dict['pool_size']} entries)")

    # 3. Certificates
    cert_paths = build_certificates(CERTS_DIR, RAW_DIR)
    print(f"Wrote {len(cert_paths)} certificates in {CERTS_DIR}")

    # 4. Catalogue v2 JSON
    cat = build_catalogue(retime=retime)
    cat_path = TARGETS_DIR / "frontier_targets_v2.json"
    cat_path.write_text(json.dumps(cat, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {cat_path} ({len(cat['targets'])} targets)")


def check_all() -> bool:
    """Verify committed files match reconstructed catalogue and selection rule."""
    cat_path = TARGETS_DIR / "frontier_targets_v2.json"
    sources_path = TARGETS_DIR / "frontier_sources_v2.json"
    pool_path = TARGETS_DIR / "ljcr_pool_v2.json"

    if not cat_path.exists() or not sources_path.exists() or not pool_path.exists():
        print("ERROR: Catalogue files missing!", file=sys.stderr)
        return False

    with cat_path.open("r", encoding="utf-8") as f:
        committed_cat = json.load(f)

    with sources_path.open("r", encoding="utf-8") as f:
        committed_sources = json.load(f)

    with pool_path.open("r", encoding="utf-8") as f:
        committed_pool = json.load(f)

    # 1. Verify sources match
    assert len(committed_sources) == len(SOURCES_META)
    for sid, meta in SOURCES_META.items():
        assert sid in committed_sources
        for k in ("url", "sha256", "accessed_at"):
            assert committed_sources[sid][k] == meta[k], f"Source {sid} mismatch on {k}"

    # 2. Verify pool matches
    rebuilt_pool = build_ljcr_pool(RAW_DIR / "coverdata.json")
    assert rebuilt_pool["pool_size"] == committed_pool["pool_size"] == 3827

    # 3. Verify selection rule on pool
    stale, active, rand_ctrl = select_covering_targets(committed_pool)
    expected_ids = set()
    for name in stale + active + rand_ctrl:
        m = re.match(r"C\((\d+),(\d+),(\d+)\)", name)
        assert m
        expected_ids.add(f"covering_C_{m.group(1)}_{m.group(2)}_{m.group(3)}")

    cat_cov_record_ids = {
        t["target_id"]
        for t in committed_cat["targets"]
        if t["family"] == "covering_design" and t["role"] == "record"
    }
    assert cat_cov_record_ids == expected_ids, (
        f"Covering record IDs mismatch: diff={cat_cov_record_ids ^ expected_ids}"
    )

    # 4. Verify reconstructed catalogue fields
    rebuilt_cat = build_catalogue(retime=False)
    assert len(rebuilt_cat["targets"]) == len(committed_cat["targets"])
    for r_t, c_t in zip(rebuilt_cat["targets"], committed_cat["targets"]):
        for k in r_t:
            if k == "verifier_runtime_s":
                assert isinstance(c_t[k], (int, float))
                assert 0.0 <= c_t[k] <= 60.0
            else:
                assert r_t[k] == c_t[k], f"Target {r_t['target_id']} mismatch on {k}"

    # 5. Load through strict schema loader
    loaded = load_frontier_catalogue(cat_path)
    assert len(loaded) == len(committed_cat["targets"])

    print("ALL CATALOGUE CHECK GATES PASSED DETERMINISTICALLY!")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Frontier Target Catalogue v2 builder and checker")
    parser.add_argument("--check", action="store_true", help="Check committed catalogue against reconstruction")
    parser.add_argument("--retime", action="store_true", help="Force remeasurement of verification runtime")
    args = parser.parse_args()

    if args.check:
        if not check_all():
            sys.exit(1)
    else:
        write_all(retime=args.retime)
        if not check_all():
            sys.exit(1)


if __name__ == "__main__":
    main()
