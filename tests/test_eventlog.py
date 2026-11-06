"""Testes do log incremental e limitado de eventos da busca."""

from __future__ import annotations

import json
import time

import pytest

from evobyte.search.eventlog import (
    EventLogError,
    EventLogPolicy,
    EventLogWriter,
)


def read_events(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_events_are_written_incrementally_before_close(tmp_path):
    path = tmp_path / "search-events.jsonl"
    writer = EventLogWriter(
        path,
        EventLogPolicy(flush_every=1),
    )

    writer.emit({"event": "start", "n": 8})
    writer.emit({"event": "maximal", "m": 10})

    before_close = read_events(path)
    assert [event["event"] for event in before_close] == ["start", "maximal"]

    stats = writer.close()
    assert stats["events_total"] == 2
    assert stats["events_written"] == 2
    assert stats["events_dropped"] == 0


def test_caps_non_key_events_and_preserves_key_events(tmp_path):
    path = tmp_path / "search-events.jsonl"
    writer = EventLogWriter(
        path,
        EventLogPolicy(max_non_key_events=5, max_bytes=10_000_000),
    )

    writer.emit({"event": "start", "n": 8})
    for index in range(10):
        writer.emit({"event": "maximal", "index": index})
    writer.emit({"event": "new_best", "best_m": 10})
    for index in range(10):
        writer.emit({"event": "perturbation", "index": index})
    writer.emit({"event": "invalid_action", "action": [0, 1]})
    writer.emit({"event": "stop", "reason": "budget"})

    stats = writer.close()
    events = read_events(path)
    names = [event["event"] for event in events]

    assert names[0] == "start"
    assert names[-1] == "log_summary"
    assert names.count("maximal") == 5
    assert names.count("perturbation") == 0
    assert names.count("new_best") == 1
    assert names.count("invalid_action") == 1
    assert names.count("stop") == 1
    assert stats["events_total"] == 24
    assert stats["events_written"] == 9
    assert stats["events_dropped"] == 15
    assert stats["non_key_written"] == 5
    assert stats["key_written"] == 4
    assert stats["truncated"] is True
    assert stats["first_dropped_index"] == 7
    assert stats["last_dropped_index"] == 22
    assert stats["key_dropped"] == 0
    assert events[-1]["aborted"] is False
    assert events[-1]["closed"] is True


def test_byte_cap_limits_non_key_bytes_but_keeps_key_events(tmp_path):
    path = tmp_path / "search-events.jsonl"
    writer = EventLogWriter(
        path,
        EventLogPolicy(max_non_key_events=1_000_000, max_bytes=500, flush_every=1),
    )

    writer.emit({"event": "start", "n": 8})
    for index in range(100):
        writer.emit({"event": "maximal", "payload": "x" * 200, "index": index})
    writer.emit({"event": "stop", "reason": "budget"})

    stats = writer.close()
    events = read_events(path)
    names = [event["event"] for event in events]

    assert stats["non_key_bytes"] <= 500
    assert stats["truncated"] is True
    assert stats["key_written"] == 2
    assert stats["events_dropped"] == 100 - stats["non_key_written"]
    assert names[0] == "start"
    assert names[-2] == "stop"
    assert names[-1] == "log_summary"


def test_interruption_writes_valid_summary(tmp_path):
    path = tmp_path / "search-events.jsonl"
    writer = EventLogWriter(path, EventLogPolicy(flush_every=1))

    writer.emit({"event": "start", "n": 8})
    writer.emit({"event": "maximal", "m": 1})
    try:
        raise RuntimeError("interrupção simulada")
    except RuntimeError:
        stats = writer.close(aborted=True)

    events = read_events(path)
    assert stats["aborted"] is True
    assert stats["closed"] is True
    assert events[-1]["event"] == "log_summary"
    assert events[-1]["aborted"] is True
    assert events[0]["event"] == "start"
    assert events[1]["event"] == "maximal"


def test_close_is_idempotent(tmp_path):
    path = tmp_path / "search-events.jsonl"
    writer = EventLogWriter(path, EventLogPolicy(flush_every=1))
    writer.emit({"event": "start", "n": 8})
    first = writer.close()
    second = writer.close(aborted=True)

    assert first["events_total"] == second["events_total"] == 1
    assert second["aborted"] is False
    assert len(read_events(path)) == 2


def test_one_million_events_are_bounded_and_dropped_without_dump(tmp_path):
    path = tmp_path / "search-events.jsonl"
    writer = EventLogWriter(
        path,
        EventLogPolicy(
            max_non_key_events=20_000,
            max_bytes=4 * 1024 * 1024,
            flush_every=256,
        ),
    )

    started = time.monotonic()
    writer.emit({"event": "start", "n": 8})
    for index in range(1_000_000):
        writer.emit({"event": "maximal", "index": index})
    writer.emit({"event": "stop", "reason": "budget"})
    stats = writer.close()
    elapsed = time.monotonic() - started

    events = read_events(path)
    assert stats["events_total"] == 1_000_002
    assert stats["non_key_written"] == 20_000
    assert stats["non_key_dropped"] == 980_000
    assert stats["events_written"] == 20_002
    assert stats["key_written"] == 2
    assert stats["truncated"] is True
    assert stats["first_dropped_index"] == 20_002
    assert stats["last_dropped_index"] == 1_000_001
    assert events[0]["event"] == "start"
    assert events[-2]["event"] == "stop"
    assert events[-1]["event"] == "log_summary"
    assert path.stat().st_size < 5 * 1024 * 1024
    assert elapsed < 10.0


def test_invalid_policy_and_events_are_rejected(tmp_path):
    with pytest.raises(EventLogError) as exc:
        EventLogPolicy(max_non_key_events=-1)
    assert exc.value.code == "INVALID_MAX_EVENTS"

    with pytest.raises(EventLogError) as exc:
        EventLogPolicy(max_bytes=0)
    assert exc.value.code == "INVALID_MAX_BYTES"

    with pytest.raises(EventLogError) as exc:
        EventLogPolicy(flush_every=0)
    assert exc.value.code == "INVALID_FLUSH_INTERVAL"

    with pytest.raises(EventLogError) as exc:
        EventLogPolicy(key_events=frozenset({"start", ""}))
    assert exc.value.code == "INVALID_KEY_EVENTS"

    path = tmp_path / "search-events.jsonl"
    writer = EventLogWriter(path, EventLogPolicy(flush_every=1))
    with pytest.raises(EventLogError) as exc:
        writer.emit("não é mapping")
    assert exc.value.code == "INVALID_EVENT"

    with pytest.raises(EventLogError) as exc:
        writer.emit({"event": "start", "bad": object()})
    assert exc.value.code == "INVALID_EVENT"

    writer.close()
    with pytest.raises(EventLogError) as exc:
        writer.emit({"event": "stop"})
    assert exc.value.code == "EVENT_LOG_CLOSED"

    with pytest.raises(EventLogError) as exc:
        EventLogWriter(path)
    assert exc.value.code == "EVENT_LOG_EXISTS"


def test_custom_key_events_are_preserved(tmp_path):
    path = tmp_path / "search-events.jsonl"
    writer = EventLogWriter(
        path,
        EventLogPolicy(
            max_non_key_events=0,
            key_events=frozenset({"start", "stop"}),
        ),
    )
    writer.emit({"event": "start"})
    writer.emit({"event": "restart"})
    writer.emit({"event": "stop"})
    stats = writer.close()

    events = read_events(path)
    names = [event["event"] for event in events]
    assert names == ["start", "stop", "log_summary"]
    assert stats["events_total"] == 3
    assert stats["events_written"] == 2
    assert stats["events_dropped"] == 1
