"""Testes da CLI de verificação e execução supervisionada (F02-T05)."""

from __future__ import annotations

import hashlib
import io
import json
import sys

from evobyte import cli
from evobyte.campaign import open_campaign
from evobyte.candidate import canonical_json_bytes

COMMIT = "a" * 40
PROTOCOL_SHA256 = "b" * 64


def valid_config(
    *,
    wall_limit_s=60,
    campaign_id="campaign-test",
    run_id="run-1",
    method="random",
    **overrides,
):
    config = {
        "schema_version": 1,
        "protocol_version": "P0-development-v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "campaign_id": campaign_id,
        "run_id": run_id,
        "code_commit": COMMIT,
        "rules_id": "girth-ge-5-v1",
        "n": 8,
        "method": method,
        "cost_mode": "cold_start",
        "seed_block": 0,
        "derived_seeds": {"search": 1, "tiebreak": 2},
        "device": "cpu",
        "compute_threads": 1,
        "budget": {
            "wall_limit_s": wall_limit_s,
            "search_stop_s": wall_limit_s * 0.9,
            "finalize_by_s": wall_limit_s * 0.95,
            "terminate_at_s": wall_limit_s * 29 / 30,
            "kill_at_s": wall_limit_s * 59 / 60,
            "checkpoint_every_s": 5,
            "training_limit_s": wall_limit_s * 0.2,
        },
        "method_parameters": {},
    }
    config.update(overrides)
    return config


def freeze_manifest(manifest):
    payload = {
        key: value
        for key, value in manifest.items()
        if key != "frozen_manifest_sha256"
    }
    digest = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    frozen = dict(payload)
    frozen["frozen_manifest_sha256"] = digest
    return frozen


def make_manifest(
    *,
    run_id="run-1",
    wall_limit_s=60,
    status="FROZEN",
    campaign_id="campaign-test",
    is_example=None,
    **overrides,
):
    manifest = {
        "schema_version": 1,
        "campaign_id": campaign_id,
        "status": status,
        "protocol_version": "P0-development-v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "absolute_wall_cap_s": 300000,
        "reserved_wall_s": wall_limit_s,
        "planned_max_experimental_launches": 1,
        "quotas_s": {"development": wall_limit_s},
        "schedule": [
            {
                "run_id": run_id,
                "stage": "development",
                "wall_limit_s": wall_limit_s,
                "max_attempts": 1,
            }
        ],
        "frozen_manifest_sha256": None,
    }
    if is_example is not None:
        manifest["is_example"] = is_example
    manifest.update(overrides)
    return freeze_manifest(manifest)


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def run_cli(*args):
    stream = io.StringIO()
    code = cli.main(list(args), stdout=stream)
    return code, stream.getvalue()


def prepare_run_files(tmp_path, *, config=None, manifest=None):
    config = valid_config() if config is None else config
    manifest = make_manifest() if manifest is None else manifest
    config_path = write_json(tmp_path / "config.json", config)
    manifest_path = write_json(tmp_path / "manifest.json", manifest)
    return config_path, manifest_path


def enable_simulated_method(monkeypatch, body="import time\ntime.sleep(0.05)\n"):
    monkeypatch.setattr(cli, "IMPLEMENTED_METHODS", frozenset({"random"}))

    def worker_command(config):
        return [sys.executable, "-c", body]

    monkeypatch.setattr(cli, "_worker_command_for_method", worker_command)
    monkeypatch.setattr(cli, "_observe_git_state", lambda: (COMMIT, True))


def test_verify_valid_candidate(tmp_path):
    payload = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": 5,
        "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]],
        "claimed_m": 5,
    }
    path = write_json(tmp_path / "candidate.json", payload)

    code, output = run_cli(
        "verify",
        str(path),
        "--expected-n",
        "5",
        "--reference",
    )

    assert code == 0
    result = json.loads(output)
    assert result["ok"] is True
    assert result["result"]["valid"] is True
    assert result["result"]["computed_m"] == 5
    assert result["result"]["expected_n"] == 5
    assert result["result"]["validator_id"] == "evobyte-reference"


def test_verify_invalid_candidate_still_completes(tmp_path):
    payload = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": 5,
        "edges": [[0, 1], [1, 2], [2, 0]],
        "claimed_m": 3,
    }
    path = write_json(tmp_path / "candidate.json", payload)

    code, output = run_cli("verify", str(path), "--expected-n", "5")

    assert code == 0
    result = json.loads(output)
    assert result["ok"] is True
    assert result["result"]["valid"] is False
    assert "C3_DETECTED" in result["summary"]


def test_verify_envelope_hash_round_trip(tmp_path):
    payload = {
        "schema_version": 1,
        "rules_id": "girth-ge-5-v1",
        "n": 5,
        "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]],
        "claimed_m": 5,
    }
    digest = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    envelope = {
        "run_id": "run-1",
        "payload": payload,
        "content_sha256": digest,
    }
    path = write_json(tmp_path / "candidate.json", envelope)

    code, output = run_cli("verify", str(path), "--expected-n", "5")
    assert code == 0
    assert json.loads(output)["result"]["valid"] is True

    envelope["content_sha256"] = "0" * 64
    write_json(path, envelope)
    code, output = run_cli("verify", str(path), "--expected-n", "5")
    assert code == 2
    assert json.loads(output)["error"]["code"] == "CANDIDATE_HASH_MISMATCH"


def test_verify_rejects_example(tmp_path):
    path = write_json(
        tmp_path / "candidate.json",
        {
            "is_example": True,
            "payload": {
                "schema_version": 1,
                "rules_id": "girth-ge-5-v1",
                "n": 5,
                "edges": [],
                "claimed_m": 0,
            },
            "content_sha256": None,
        },
    )

    code, output = run_cli("verify", str(path), "--expected-n", "5")

    assert code == 2
    assert json.loads(output)["error"]["code"] == "EXAMPLE_NOT_ALLOWED"


def test_verify_rejects_invalid_json(tmp_path):
    path = tmp_path / "candidate.json"
    path.write_text("{invalido", encoding="utf-8")

    code, output = run_cli("verify", str(path), "--expected-n", "5")

    assert code == 2
    assert json.loads(output)["error"]["code"] == "INVALID_JSON"


def test_verify_requires_expected_n(tmp_path):
    path = write_json(tmp_path / "candidate.json", {})

    code, output = run_cli("verify", str(path))

    assert code == 2
    assert json.loads(output)["error"]["code"] == "INVALID_ARGUMENTS"


def test_verify_rejects_missing_file(tmp_path):
    code, output = run_cli(
        "verify",
        str(tmp_path / "nao-existe.json"),
        "--expected-n",
        "5",
    )

    assert code == 2
    assert json.loads(output)["error"]["code"] == "FILE_NOT_FOUND"


def test_verify_non_object_payload_is_rejected_by_reference(tmp_path):
    path = write_json(tmp_path / "candidate.json", [])

    code, output = run_cli("verify", str(path), "--expected-n", "5")

    assert code == 0
    result = json.loads(output)
    assert result["result"]["valid"] is False
    assert result["result"]["violations"][0]["code"] == "INVALID_PAYLOAD_TYPE"


def test_help_and_unknown_command(tmp_path):
    code, output = run_cli("--help")
    assert code == 0
    assert "verify" in output
    assert "run" in output

    code, output = run_cli("verify", "--help")
    assert code == 0
    assert "--expected-n" in output

    code, output = run_cli("bogus")
    assert code == 2
    assert json.loads(output)["error"]["code"] == "INVALID_ARGUMENTS"


def test_analyze_is_explicitly_not_implemented(tmp_path):
    manifest_path = write_json(tmp_path / "manifest.json", make_manifest())

    code, output = run_cli(
        "analyze",
        "--manifest",
        str(manifest_path),
        "--output",
        str(tmp_path / "analysis"),
    )

    assert code == 2
    assert json.loads(output)["error"]["code"] == "COMMAND_NOT_IMPLEMENTED"


def test_campaign_reports_ledger(tmp_path):
    manifest_path = write_json(tmp_path / "manifest.json", make_manifest())
    ledger_path = tmp_path / "ledger.json"

    code, output = run_cli(
        "campaign",
        "--manifest",
        str(manifest_path),
        "--ledger",
        str(ledger_path),
    )

    assert code == 0
    result = json.loads(output)
    assert result["ok"] is True
    assert result["campaign_id"] == "campaign-test"
    assert result["ledger"]["global"]["limit_seconds"] == 60.0
    assert ledger_path.exists()


def test_campaign_rejects_example_and_unfrozen(tmp_path):
    example_path = write_json(
        tmp_path / "manifest-example.json",
        make_manifest(is_example=True),
    )
    code, output = run_cli(
        "campaign",
        "--manifest",
        str(example_path),
        "--ledger",
        str(tmp_path / "ledger-a.json"),
    )
    assert code == 2
    assert json.loads(output)["error"]["code"] == "EXAMPLE_NOT_ALLOWED"

    unfrozen_path = write_json(
        tmp_path / "manifest-unfrozen.json",
        make_manifest(status="PLANNED"),
    )
    code, output = run_cli(
        "campaign",
        "--manifest",
        str(unfrozen_path),
        "--ledger",
        str(tmp_path / "ledger-b.json"),
    )
    assert code == 2
    assert json.loads(output)["error"]["code"] == "MANIFEST_NOT_FROZEN"


def test_run_rejects_unimplemented_method(tmp_path):
    config_path, manifest_path = prepare_run_files(tmp_path)
    ledger_path = tmp_path / "ledger.json"

    code, output = run_cli(
        "run",
        "--config",
        str(config_path),
        "--manifest",
        str(manifest_path),
        "--ledger",
        str(ledger_path),
        "--runs-dir",
        str(tmp_path / "runs"),
    )

    assert code == 2
    assert json.loads(output)["error"]["code"] == "METHOD_NOT_IMPLEMENTED"
    assert not ledger_path.exists()


def test_run_rejects_missing_method(tmp_path):
    config = valid_config()
    config.pop("method")
    config_path, manifest_path = prepare_run_files(tmp_path, config=config)

    code, output = run_cli(
        "run",
        "--config",
        str(config_path),
        "--manifest",
        str(manifest_path),
    )

    assert code == 2
    assert json.loads(output)["error"]["code"] == "MISSING_FIELD"


def test_run_rejects_unfrozen_manifest(tmp_path):
    config_path, manifest_path = prepare_run_files(
        tmp_path,
        manifest=make_manifest(status="PLANNED"),
    )

    code, output = run_cli(
        "run",
        "--config",
        str(config_path),
        "--manifest",
        str(manifest_path),
    )

    assert code == 2
    assert json.loads(output)["error"]["code"] == "MANIFEST_NOT_FROZEN"


def test_run_rejects_example_config(tmp_path):
    config_path, manifest_path = prepare_run_files(
        tmp_path,
        config=valid_config(is_example=True),
    )

    code, output = run_cli(
        "run",
        "--config",
        str(config_path),
        "--manifest",
        str(manifest_path),
    )

    assert code == 2
    assert json.loads(output)["error"]["code"] == "EXAMPLE_NOT_ALLOWED"


def test_run_rejects_campaign_mismatch(tmp_path):
    config_path, manifest_path = prepare_run_files(
        tmp_path,
        config=valid_config(campaign_id="outra-campanha"),
    )

    code, output = run_cli(
        "run",
        "--config",
        str(config_path),
        "--manifest",
        str(manifest_path),
    )

    assert code == 2
    assert json.loads(output)["error"]["code"] == "CAMPAIGN_MISMATCH"


def test_run_rejects_run_not_in_manifest(tmp_path):
    config_path, manifest_path = prepare_run_files(
        tmp_path,
        config=valid_config(run_id="run-2"),
    )

    code, output = run_cli(
        "run",
        "--config",
        str(config_path),
        "--manifest",
        str(manifest_path),
    )

    assert code == 2
    assert json.loads(output)["error"]["code"] == "RUN_NOT_IN_MANIFEST"


def test_run_rejects_limit_mismatch(tmp_path):
    config_path, manifest_path = prepare_run_files(
        tmp_path,
        config=valid_config(wall_limit_s=30),
        manifest=make_manifest(wall_limit_s=60),
    )

    code, output = run_cli(
        "run",
        "--config",
        str(config_path),
        "--manifest",
        str(manifest_path),
    )

    assert code == 2
    assert json.loads(output)["error"]["code"] == "RUN_LIMIT_MISMATCH"


def test_run_rejects_dirty_worktree(tmp_path, monkeypatch):
    config_path, manifest_path = prepare_run_files(tmp_path)
    monkeypatch.setattr(cli, "IMPLEMENTED_METHODS", frozenset({"random"}))
    monkeypatch.setattr(
        cli,
        "_worker_command_for_method",
        lambda config: [sys.executable, "-c", "pass"],
    )
    monkeypatch.setattr(cli, "_observe_git_state", lambda: (COMMIT, False))
    ledger_path = tmp_path / "ledger.json"

    code, output = run_cli(
        "run",
        "--config",
        str(config_path),
        "--manifest",
        str(manifest_path),
        "--ledger",
        str(ledger_path),
    )

    assert code == 2
    assert json.loads(output)["error"]["code"] == "DIRTY_WORKTREE"
    assert not ledger_path.exists()


def test_run_rejects_commit_mismatch(tmp_path, monkeypatch):
    config_path, manifest_path = prepare_run_files(tmp_path)
    monkeypatch.setattr(cli, "IMPLEMENTED_METHODS", frozenset({"random"}))
    monkeypatch.setattr(
        cli,
        "_worker_command_for_method",
        lambda config: [sys.executable, "-c", "pass"],
    )
    monkeypatch.setattr(cli, "_observe_git_state", lambda: ("c" * 40, True))
    ledger_path = tmp_path / "ledger.json"

    code, output = run_cli(
        "run",
        "--config",
        str(config_path),
        "--manifest",
        str(manifest_path),
        "--ledger",
        str(ledger_path),
    )

    assert code == 2
    assert json.loads(output)["error"]["code"] == "CODE_COMMIT_MISMATCH"
    assert not ledger_path.exists()


def test_run_simulated_completes_and_uses_supervisor(tmp_path, monkeypatch):
    config_path, manifest_path = prepare_run_files(tmp_path)
    enable_simulated_method(monkeypatch)
    ledger_path = tmp_path / "ledger.json"
    runs_dir = tmp_path / "runs"

    code, output = run_cli(
        "run",
        "--config",
        str(config_path),
        "--manifest",
        str(manifest_path),
        "--ledger",
        str(ledger_path),
        "--runs-dir",
        str(runs_dir),
    )

    assert code == 0
    result = json.loads(output)
    assert result["ok"] is True
    assert result["result"]["status"] == "completed"
    assert result["result"]["exit_code"] == 0
    assert result["reconciliation"]["status"] == "completed"

    run_dir = runs_dir / "campaign-test" / "run-1"
    assert (run_dir / "config.json").exists()
    assert (run_dir / "environment.json").exists()
    assert (run_dir / "events.jsonl").exists()
    assert (run_dir / "checkpoint.json").exists()
    assert (run_dir / "worker.stdout.log").exists()
    assert (run_dir / "worker.stderr.log").exists()

    certificate_path = run_dir / "empty-certificate" / "certificate.json"
    assert certificate_path.exists()
    certificate = json.loads(certificate_path.read_bytes())
    assert certificate["status"] == "CERTIFIED"

    ledger = json.loads(ledger_path.read_bytes())
    assert ledger["reserved_seconds"] == 0.0
    assert ledger["reservations"] == {}
    assert ledger["consumed_seconds"] > 0.0

    inventory = json.loads((run_dir / "inventory.json").read_bytes())
    assert "checkpoint.json" in inventory["files"]
    assert "config.json" in inventory["files"]
    assert (run_dir / "events.jsonl").read_text(encoding="utf-8").strip()


def test_run_simulated_failure_exits_three(tmp_path, monkeypatch):
    config_path, manifest_path = prepare_run_files(tmp_path)
    enable_simulated_method(monkeypatch, body="import sys\nsys.exit(3)\n")
    ledger_path = tmp_path / "ledger.json"

    code, output = run_cli(
        "run",
        "--config",
        str(config_path),
        "--manifest",
        str(manifest_path),
        "--ledger",
        str(ledger_path),
        "--runs-dir",
        str(tmp_path / "runs"),
    )

    assert code == 3
    result = json.loads(output)
    assert result["ok"] is False
    assert result["result"]["status"] == "crashed"
    assert result["reconciliation"]["status"] == "crashed"

    ledger = json.loads(ledger_path.read_bytes())
    assert ledger["reservations"] == {}
    assert ledger["launches"] == 1
    assert ledger["consumed_seconds"] > 0.0


def test_run_reservation_blocks_second_controller(tmp_path, monkeypatch):
    config_path, manifest_path = prepare_run_files(tmp_path)
    enable_simulated_method(monkeypatch)
    ledger_path = tmp_path / "ledger.json"
    manifest = json.loads(manifest_path.read_bytes())

    controller = open_campaign(manifest, ledger_path)
    try:
        code, output = run_cli(
            "run",
            "--config",
            str(config_path),
            "--manifest",
            str(manifest_path),
            "--ledger",
            str(ledger_path),
            "--runs-dir",
            str(tmp_path / "runs"),
        )
        assert code == 2
        assert json.loads(output)["error"]["code"] == "CAMPAIGN_LOCKED"
    finally:
        controller.close()


def test_run_failure_after_reservation_releases_attempt(tmp_path, monkeypatch):
    config_path, manifest_path = prepare_run_files(tmp_path)
    enable_simulated_method(monkeypatch)
    ledger_path = tmp_path / "ledger.json"
    run_dir = tmp_path / "runs" / "campaign-test" / "run-1"
    run_dir.mkdir(parents=True)
    (run_dir / "existente.txt").write_text("dados", encoding="utf-8")

    code, output = run_cli(
        "run",
        "--config",
        str(config_path),
        "--manifest",
        str(manifest_path),
        "--ledger",
        str(ledger_path),
        "--runs-dir",
        str(tmp_path / "runs"),
    )

    assert code == 2
    assert json.loads(output)["error"]["code"] == "RUN_EXISTS"
    ledger = json.loads(ledger_path.read_bytes())
    assert ledger["reservations"] == {}
    assert ledger["launches"] == 1
    assert ledger["consumed_seconds"] == 0.0
