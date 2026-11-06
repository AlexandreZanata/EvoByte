"""Testes de configuração, ambiente, eventos e inventário (F02-T01)."""

from __future__ import annotations

import hashlib
import json
import os

import pytest

from evobyte import __version__
from evobyte.candidate import canonical_json_bytes
from evobyte.records import (
    CONFIG_FILENAME,
    ENVIRONMENT_FILENAME,
    EVENTS_FILENAME,
    INVENTORY_FILENAME,
    RecordsError,
    RunConfig,
    _atomic_write_bytes,
    capture_environment,
    config_bytes,
    initialize_run,
    load_config,
    read_events,
    resume_run,
    verify_inventory,
    write_inventory,
)

COMMIT = "a" * 40
PROTOCOL_SHA256 = "b" * 64


def valid_config():
    return {
        "schema_version": 1,
        "protocol_version": "P0-development-v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "campaign_id": "campaign-1",
        "run_id": "run-1",
        "code_commit": COMMIT,
        "rules_id": "girth-ge-5-v1",
        "n": 8,
        "method": "random",
        "cost_mode": "cold_start",
        "seed_block": 0,
        "derived_seeds": {
            "data": 0,
            "training": 1,
            "search": 2,
            "tiebreak": 3,
        },
        "device": "cpu",
        "compute_threads": 1,
        "budget": {
            "wall_limit_s": 60,
            "search_stop_s": 54,
            "finalize_by_s": 57,
            "terminate_at_s": 58,
            "kill_at_s": 59,
            "checkpoint_every_s": 5,
            "training_limit_s": 12,
        },
        "method_parameters": {},
    }


def mutated_config(**overrides):
    config = valid_config()
    config.update(overrides)
    return config


def config_with_budget(**overrides):
    config = valid_config()
    budget = dict(config["budget"])
    budget.update(overrides)
    config["budget"] = budget
    return config


def reverse_mapping(mapping):
    reversed_mapping = {}
    for key, value in reversed(list(mapping.items())):
        reversed_mapping[key] = reverse_mapping(value) if isinstance(value, dict) else value
    return reversed_mapping


def initialize(tmp_path, config=None, **kwargs):
    options = {
        "observed_commit": COMMIT,
        "worktree_clean": True,
        "environment": {"gpu": None, "unavailable": {"gpu": "not_queried"}},
    }
    options.update(kwargs)
    return initialize_run(
        valid_config() if config is None else config,
        tmp_path / "run",
        **options,
    )


@pytest.fixture
def recorder(tmp_path):
    return initialize(tmp_path)


def test_config_is_valid_and_hash_is_stable():
    first = RunConfig.from_mapping(valid_config())
    second = RunConfig.from_mapping(reverse_mapping(valid_config()))

    assert first.payload == second.payload
    assert first.sha256 == second.sha256
    assert first.sha256 == hashlib.sha256(canonical_json_bytes(first.payload)).hexdigest()
    assert "config_sha256" not in first.payload


def test_config_canonical_bytes_are_stable():
    first = RunConfig.from_mapping(valid_config())
    second = RunConfig.from_mapping(reverse_mapping(valid_config()))

    assert config_bytes(first) == config_bytes(second)
    assert config_bytes(first) == canonical_json_bytes(first.payload)
    assert not config_bytes(first).endswith(b"\n")


def test_initialize_writes_evidence_and_inventory(tmp_path):
    environment = {
        "gpu": None,
        "unavailable": {"gpu": "not_queried"},
        "packages": {"evobyte": __version__},
    }
    recorder = initialize(tmp_path, environment=environment)
    directory = recorder.directory

    assert directory == tmp_path / "run"
    assert (directory / CONFIG_FILENAME).read_bytes() == config_bytes(recorder.config)
    assert (directory / ENVIRONMENT_FILENAME).read_bytes() == canonical_json_bytes(
        environment
    )
    assert (directory / EVENTS_FILENAME).read_bytes() == b""
    assert read_events(directory) == ()

    inventory = verify_inventory(directory)
    assert set(inventory["files"]) == {
        CONFIG_FILENAME,
        ENVIRONMENT_FILENAME,
        EVENTS_FILENAME,
    }
    assert INVENTORY_FILENAME not in inventory["files"]
    assert inventory["files"][CONFIG_FILENAME] == recorder.config.sha256
    assert recorder.config_sha256 == recorder.config.sha256
    assert recorder.next_sequence == 1


def test_capture_environment_marks_unavailable(monkeypatch):
    monkeypatch.setenv("EVOBYTE_TEST_SECRET", "segredo-que-nao-pode-vazar")
    environment = capture_environment()

    assert environment["python"]["version"]
    assert environment["packages"]["evobyte"] == __version__
    assert environment["gpu"] is None
    assert environment["cuda"] is None
    assert environment["unavailable"]["gpu"] == "not_queried"
    assert environment["unavailable"]["cuda"] == "not_queried"

    serialized = json.dumps(environment)
    assert "segredo-que-nao-pode-vazar" not in serialized
    assert "EVOBYTE_TEST_SECRET" not in serialized


def test_initialize_rejects_example(tmp_path):
    config = mutated_config(is_example=True)

    with pytest.raises(RecordsError) as exc:
        initialize(tmp_path, config)

    assert exc.value.code == "EXAMPLE_NOT_ALLOWED"
    assert not (tmp_path / "run").exists()


def test_initialize_rejects_dirty_worktree(tmp_path):
    with pytest.raises(RecordsError) as exc:
        initialize(tmp_path, worktree_clean=False)

    assert exc.value.code == "DIRTY_WORKTREE"
    assert not (tmp_path / "run").exists()


def test_initialize_rejects_commit_mismatch(tmp_path):
    with pytest.raises(RecordsError) as exc:
        initialize(tmp_path, observed_commit="c" * 40)

    assert exc.value.code == "CODE_COMMIT_MISMATCH"
    assert not (tmp_path / "run").exists()


def test_initialize_rejects_existing_run(tmp_path):
    initialize(tmp_path)

    with pytest.raises(RecordsError) as exc:
        initialize(tmp_path)

    assert exc.value.code == "RUN_EXISTS"


def test_initialize_rejects_file_as_output(tmp_path):
    output = tmp_path / "run"
    output.write_text("arquivo", encoding="utf-8")

    with pytest.raises(RecordsError) as exc:
        initialize_run(
            valid_config(),
            output,
            observed_commit=COMMIT,
            worktree_clean=True,
            environment={},
        )

    assert exc.value.code == "OUTPUT_NOT_DIRECTORY"


INVALID_CONFIG_CASES = [
    pytest.param(lambda: [], "CONFIG_NOT_MAPPING", id="not-mapping"),
    pytest.param(
        lambda: mutated_config(is_example=False),
        "EXAMPLE_NOT_ALLOWED",
        id="example-false",
    ),
    pytest.param(
        lambda: mutated_config(extra="x"),
        "UNKNOWN_FIELD",
        id="unknown-field",
    ),
    pytest.param(
        lambda: {
            key: value
            for key, value in valid_config().items()
            if key != "method"
        },
        "MISSING_FIELD",
        id="missing-field",
    ),
    pytest.param(
        lambda: mutated_config(schema_version=2),
        "INVALID_SCHEMA_VERSION",
        id="schema",
    ),
    pytest.param(
        lambda: mutated_config(protocol_version=""),
        "INVALID_PROTOCOL_VERSION",
        id="protocol-version",
    ),
    pytest.param(
        lambda: mutated_config(protocol_sha256="abc"),
        "INVALID_PROTOCOL_SHA256",
        id="protocol-hash",
    ),
    pytest.param(
        lambda: mutated_config(campaign_id=""),
        "INVALID_CAMPAIGN_ID",
        id="campaign-id",
    ),
    pytest.param(
        lambda: mutated_config(run_id=""),
        "INVALID_RUN_ID",
        id="run-id",
    ),
    pytest.param(
        lambda: mutated_config(code_commit="XYZ"),
        "INVALID_CODE_COMMIT",
        id="commit",
    ),
    pytest.param(
        lambda: mutated_config(rules_id="outra-regra"),
        "UNEXPECTED_RULES_ID",
        id="rules",
    ),
    pytest.param(lambda: mutated_config(n=7), "INVALID_N", id="n"),
    pytest.param(
        lambda: mutated_config(method="desconhecido"),
        "INVALID_METHOD",
        id="method",
    ),
    pytest.param(
        lambda: mutated_config(cost_mode="startup"),
        "INVALID_COST_MODE",
        id="cost-mode",
    ),
    pytest.param(
        lambda: mutated_config(seed_block=-1),
        "INVALID_SEED_BLOCK",
        id="seed-block",
    ),
    pytest.param(
        lambda: mutated_config(derived_seeds={}),
        "INVALID_DERIVED_SEEDS",
        id="seeds-empty",
    ),
    pytest.param(
        lambda: mutated_config(derived_seeds={"search": True}),
        "INVALID_DERIVED_SEEDS",
        id="seeds-bool",
    ),
    pytest.param(
        lambda: mutated_config(device=""),
        "INVALID_DEVICE",
        id="device",
    ),
    pytest.param(
        lambda: mutated_config(compute_threads=0),
        "INVALID_COMPUTE_THREADS",
        id="threads",
    ),
    pytest.param(
        lambda: config_with_budget(finalize_by_s=53),
        "INVALID_BUDGET",
        id="budget-order",
    ),
    pytest.param(
        lambda: config_with_budget(wall_limit_s=True),
        "INVALID_BUDGET",
        id="budget-bool",
    ),
    pytest.param(
        lambda: {
            **valid_config(),
            "budget": {
                key: value
                for key, value in valid_config()["budget"].items()
                if key != "checkpoint_every_s"
            },
        },
        "INVALID_BUDGET",
        id="budget-missing",
    ),
    pytest.param(
        lambda: mutated_config(method_parameters=[]),
        "INVALID_METHOD_PARAMETERS",
        id="parameters-type",
    ),
    pytest.param(
        lambda: mutated_config(method_parameters={"bad": {1, 2}}),
        "INVALID_CONFIG_JSON",
        id="parameters-json",
    ),
]


@pytest.mark.parametrize("builder, expected_code", INVALID_CONFIG_CASES)
def test_invalid_config_is_rejected(builder, expected_code):
    with pytest.raises(RecordsError) as exc:
        RunConfig.from_mapping(builder())

    assert exc.value.code == expected_code


def test_events_are_ordered_and_append_only(recorder):
    first = recorder.append_event(
        "start",
        elapsed_seconds=0.0,
        candidate_sha256=None,
    )
    second = recorder.append_event(
        "search",
        elapsed_seconds=1.5,
        evaluations=3,
    )
    third = recorder.append_event(
        "checkpoint",
        elapsed_seconds=2.0,
        candidate_sha256="d" * 64,
    )

    assert first["sequence"] == 1
    assert second["sequence"] == 2
    assert third["sequence"] == 3
    assert recorder.next_sequence == 4

    events = read_events(recorder.directory)
    assert [event["sequence"] for event in events] == [1, 2, 3]
    assert [event["stage"] for event in events] == ["start", "search", "checkpoint"]
    assert events[1]["evaluations"] == 3


def test_event_rejects_reserved_fields(recorder):
    with pytest.raises(RecordsError) as exc:
        recorder.append_event("start", sequence=10)
    assert exc.value.code == "INVALID_EVENT"

    with pytest.raises(RecordsError) as exc:
        recorder.append_event("")
    assert exc.value.code == "INVALID_EVENT"

    with pytest.raises(RecordsError) as exc:
        recorder.append_event("start", bad=object())
    assert exc.value.code == "INVALID_EVENT"

    assert read_events(recorder.directory) == ()
    assert recorder.next_sequence == 1


def test_event_append_failure_preserves_previous_events(recorder, monkeypatch):
    recorder.append_event("start", elapsed_seconds=0.0)
    before = (recorder.directory / EVENTS_FILENAME).read_bytes()

    real_write = os.write
    calls = {"count": 0}

    def partial_write(descriptor, data):
        calls["count"] += 1
        if calls["count"] == 1:
            return real_write(descriptor, data[:1])
        raise OSError("falha simulada")

    monkeypatch.setattr("evobyte.records.os.write", partial_write)

    with pytest.raises(RecordsError) as exc:
        recorder.append_event("search", elapsed_seconds=1.0)

    assert exc.value.code == "EVENT_WRITE_FAILED"
    assert (recorder.directory / EVENTS_FILENAME).read_bytes() == before
    events = read_events(recorder.directory)
    assert [event["stage"] for event in events] == ["start"]
    assert recorder.next_sequence == 2


def test_read_events_rejects_out_of_order(recorder):
    recorder.append_event("start")
    recorder.append_event("search")

    path = recorder.directory / EVENTS_FILENAME
    lines = path.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["sequence"] = 7
    path.write_text(
        json.dumps(first) + "\n" + lines[1] + "\n",
        encoding="utf-8",
    )

    with pytest.raises(RecordsError) as exc:
        read_events(recorder.directory)

    assert exc.value.code == "EVENT_LOG_INVALID"


def test_events_allow_unicode_line_separator(recorder):
    recorder.append_event("note", text="linha\u2028separador")

    events = read_events(recorder.directory)

    assert len(events) == 1
    assert events[0]["text"] == "linha\u2028separador"


def test_read_events_rejects_invalid_utf8(recorder):
    (recorder.directory / EVENTS_FILENAME).write_bytes(b"\xff\n")

    with pytest.raises(RecordsError) as exc:
        read_events(recorder.directory)

    assert exc.value.code == "EVENT_LOG_MISSING_OR_INVALID"


def test_atomic_write_preserves_previous_file(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    path.write_bytes(b"antigo")

    def fail_replace(source, destination):
        raise OSError("falha simulada")

    monkeypatch.setattr("evobyte.records.os.replace", fail_replace)

    with pytest.raises(OSError):
        _atomic_write_bytes(path, b"novo")

    assert path.read_bytes() == b"antigo"
    assert list(tmp_path.glob("*.tmp")) == []


def test_verify_inventory_detects_corruption(recorder):
    (recorder.directory / CONFIG_FILENAME).write_bytes(b"{}")

    with pytest.raises(RecordsError) as exc:
        verify_inventory(recorder.directory)

    assert exc.value.code == "INVENTORY_MISMATCH"


def test_verify_inventory_detects_missing_and_extra_files(tmp_path):
    recorder = initialize(tmp_path)
    (recorder.directory / ENVIRONMENT_FILENAME).unlink()

    with pytest.raises(RecordsError) as exc:
        verify_inventory(recorder.directory)
    assert exc.value.code == "INVENTORY_MISMATCH"

    recorder2 = initialize_run(
        valid_config(),
        tmp_path / "run2",
        observed_commit=COMMIT,
        worktree_clean=True,
        environment={},
    )
    extra = recorder2.directory / "extra.txt"
    extra.write_text("extra", encoding="utf-8")

    with pytest.raises(RecordsError) as exc:
        verify_inventory(recorder2.directory)
    assert exc.value.code == "INVENTORY_MISMATCH"


def test_inventory_updates_after_events(recorder):
    recorder.append_event("start")
    inventory = write_inventory(recorder.directory)

    assert inventory["files"][EVENTS_FILENAME] == hashlib.sha256(
        (recorder.directory / EVENTS_FILENAME).read_bytes()
    ).hexdigest()
    verify_inventory(recorder.directory)


def test_resume_run_continues_sequence(tmp_path):
    recorder = initialize(tmp_path)
    recorder.append_event("start")
    recorder.append_event("search")
    recorder.write_inventory()

    resumed = resume_run(recorder.directory)
    assert resumed.next_sequence == 3
    assert resumed.config.sha256 == recorder.config.sha256

    resumed.append_event("stop")
    resumed.write_inventory()

    events = read_events(recorder.directory)
    assert [event["sequence"] for event in events] == [1, 2, 3]


def test_resume_run_rejects_stale_inventory(recorder):
    recorder.append_event("start")

    with pytest.raises(RecordsError) as exc:
        resume_run(recorder.directory)

    assert exc.value.code == "INVENTORY_MISMATCH"


def test_load_config_round_trip(recorder):
    loaded = load_config(recorder.directory)

    assert loaded.payload == recorder.config.payload
    assert loaded.sha256 == recorder.config.sha256
    assert config_bytes(loaded) == config_bytes(recorder.config)
