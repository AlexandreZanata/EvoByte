"""Testes de supervisão de trabalhador e encerramento seguro (F02-T03)."""

from __future__ import annotations

import json
import os
import signal
import sys
import time

import pytest

import evobyte.supervisor as supervisor_module
from evobyte.budget import Budget
from evobyte.supervisor import (
    COMPLETED,
    CRASHED,
    EXTERNAL_FAILURE,
    OOM,
    STOP_FILENAME,
    TIMEOUT,
    SupervisorError,
    _write_json_atomic,
    run_supervised,
)


def make_budget(limit_seconds):
    return Budget(time.monotonic(), limit_seconds)


def run_worker(tmp_path, code, *, limit_seconds=1.0, args=(), **kwargs):
    checkpoint = tmp_path / "checkpoint.json"
    options = {
        "poll_interval_seconds": 0.01,
        "observation_interval_seconds": 0.02,
        "checkpoint_interval_seconds": 0.1,
    }
    options.update(kwargs)
    command = [sys.executable, "-c", code, *args]
    return run_supervised(
        command,
        make_budget(limit_seconds),
        checkpoint,
        **options,
    )


def wait_pid_gone(pid, timeout_seconds=2.0):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.01)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    return False


def test_worker_completes_before_budget(tmp_path):
    result = run_worker(
        tmp_path,
        "import time\ntime.sleep(0.05)\nprint('saida-teste', flush=True)\n",
        limit_seconds=1.0,
    )

    assert result.status == COMPLETED
    assert result.exit_code == 0
    assert result.signals == ()
    assert result.reasons == ()
    assert result.timed_out is False
    assert result.t0 > 0.0
    assert result.overrun_seconds == 0.0
    assert result.worker_still_alive is False
    assert result.process_group_empty is True
    assert result.descendants_seen == 0
    assert result.preflight_ok is None
    assert result.gpu is None
    assert result.unavailable["gpu"] == "not_queried"
    assert result.unavailable["cuda"] == "not_queried"
    assert "saida-teste" in (tmp_path / "worker.stdout.log").read_text(
        encoding="utf-8"
    )

    checkpoint = json.loads((tmp_path / "checkpoint.json").read_text(encoding="utf-8"))
    assert checkpoint["status"] == COMPLETED
    assert checkpoint["exit_code"] == 0
    assert result.checkpoints_written >= 3


def test_worker_resources_are_observed(tmp_path):
    result = run_worker(
        tmp_path,
        (
            "import time\n"
            "end = time.monotonic() + 0.2\n"
            "while time.monotonic() < end:\n"
            "    pass\n"
        ),
        limit_seconds=1.0,
    )

    assert result.status == COMPLETED
    assert result.cpu_seconds is not None
    assert result.cpu_seconds >= 0.0
    assert result.max_rss_bytes is not None
    assert result.max_rss_bytes > 0


def test_worker_failure_is_crashed(tmp_path):
    result = run_worker(tmp_path, "import sys\nsys.exit(3)\n")

    assert result.status == CRASHED
    assert result.exit_code == 3
    assert "NONZERO_EXIT" in result.reasons
    assert result.process_group_empty is True


def test_worker_that_ignores_stop_gets_term_and_timeout(tmp_path):
    result = run_worker(
        tmp_path,
        "import time\ntime.sleep(30)\n",
        limit_seconds=2.0,
    )

    assert result.status == TIMEOUT
    assert result.timed_out is True
    assert "stop" in result.signals
    assert "term" in result.signals
    assert result.exit_code in (-signal.SIGTERM, -signal.SIGKILL)
    assert result.worker_still_alive is False
    assert result.process_group_empty is True


def test_worker_that_ignores_term_gets_kill(tmp_path):
    result = run_worker(
        tmp_path,
        (
            "import signal\n"
            "import time\n"
            "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "time.sleep(30)\n"
        ),
        limit_seconds=1.0,
    )

    assert result.status == TIMEOUT
    assert result.timed_out is True
    assert "term" in result.signals
    assert "kill" in result.signals
    assert result.exit_code == -signal.SIGKILL
    assert result.worker_still_alive is False
    assert result.process_group_empty is True


def test_stop_file_allows_cooperative_exit(tmp_path):
    stop_path = tmp_path / STOP_FILENAME
    result = run_worker(
        tmp_path,
        (
            "import pathlib\n"
            "import sys\n"
            "import time\n"
            "stop = pathlib.Path(sys.argv[1])\n"
            "while not stop.exists():\n"
            "    time.sleep(0.005)\n"
            "raise SystemExit(0)\n"
        ),
        limit_seconds=2.0,
        args=(str(stop_path),),
        observation_interval_seconds=10.0,
    )

    assert result.status == COMPLETED
    assert result.exit_code == 0
    assert result.signals == ("stop",)
    assert result.timed_out is False
    assert stop_path.exists()


def test_orphan_child_is_terminated(tmp_path):
    child_pid_path = tmp_path / "child.pid"
    result = run_worker(
        tmp_path,
        (
            "import subprocess\n"
            "import sys\n"
            "child = subprocess.Popen([\n"
            "    sys.executable,\n"
            "    '-c',\n"
            "    'import signal, time; "
            "signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)',\n"
            "])\n"
            "open(sys.argv[1], 'w').write(str(child.pid))\n"
        ),
        limit_seconds=1.0,
        args=(str(child_pid_path),),
        descendant_grace_seconds=0.2,
        kill_grace_seconds=0.5,
    )

    assert result.status == CRASHED
    assert "ORPHAN_DESCENDANTS" in result.reasons
    assert result.descendants_seen is not None
    assert result.descendants_seen >= 1
    assert result.process_group_empty is True

    child_pid = int(child_pid_path.read_text(encoding="utf-8"))
    assert wait_pid_gone(child_pid)


def test_external_sigkill_is_reported_as_oom(tmp_path):
    result = run_worker(
        tmp_path,
        "import os\nimport signal\nos.kill(os.getpid(), signal.SIGKILL)\n",
    )

    assert result.status == OOM
    assert result.exit_code == -signal.SIGKILL
    assert "POSSIBLE_OOM" in result.reasons


def test_preflight_runs_before_worker(tmp_path):
    marker = tmp_path / "empty-certificate.json"

    def preflight():
        marker.write_text("{}\n", encoding="utf-8")

    result = run_worker(
        tmp_path,
        "import time\ntime.sleep(0.05)\n",
        preflight=preflight,
    )

    assert result.status == COMPLETED
    assert result.preflight_ok is True
    assert marker.exists()


def test_preflight_failure_prevents_worker_start(tmp_path):
    def preflight():
        raise RuntimeError("preflight falhou")

    result = run_worker(
        tmp_path,
        "import time\ntime.sleep(0.05)\n",
        preflight=preflight,
    )

    assert result.status == EXTERNAL_FAILURE
    assert result.preflight_ok is False
    assert "PREFLIGHT_FAILED" in result.reasons
    assert "preflight falhou" in result.error
    assert result.worker_pid is None
    assert not (tmp_path / "worker.stdout.log").exists()


def test_worker_start_failure(tmp_path):
    checkpoint = tmp_path / "checkpoint.json"

    result = run_supervised(
        ["/caminho/inexistente/worker"],
        make_budget(1.0),
        checkpoint,
        poll_interval_seconds=0.01,
        observation_interval_seconds=0.02,
        checkpoint_interval_seconds=0.1,
    )

    assert result.status == EXTERNAL_FAILURE
    assert "WORKER_START_FAILED" in result.reasons
    assert result.worker_pid is None
    assert result.error


def test_budget_exhausted_before_start(tmp_path):
    checkpoint = tmp_path / "checkpoint.json"
    t0 = time.monotonic() - 2.0
    budget = Budget(t0, 1.0)

    result = run_supervised(
        [sys.executable, "-c", "import time; time.sleep(0.05)"],
        budget,
        checkpoint,
    )

    assert result.status == TIMEOUT
    assert "BUDGET_EXHAUSTED_BEFORE_START" in result.reasons
    assert result.worker_pid is None
    assert result.checkpoints_written >= 2


def test_checkpoint_write_is_atomic(tmp_path, monkeypatch):
    path = tmp_path / "checkpoint.json"
    _write_json_atomic(path, {"status": "running", "value": 1})
    before = path.read_bytes()

    def fail_replace(source, destination):
        raise OSError("falha simulada")

    monkeypatch.setattr("evobyte.supervisor.os.replace", fail_replace)

    with pytest.raises(OSError):
        _write_json_atomic(path, {"status": "completed", "value": 2})

    assert path.read_bytes() == before
    assert list(tmp_path.glob("*.tmp")) == []


def test_checkpoint_failure_does_not_leave_worker(tmp_path, monkeypatch):
    pid_path = tmp_path / "worker.pid"
    checkpoint = tmp_path / "checkpoint.json"
    command = [
        sys.executable,
        "-c",
        (
            "import os, sys, time\n"
            "open(sys.argv[1], 'w').write(str(os.getpid()))\n"
            "time.sleep(30)\n"
        ),
        str(pid_path),
    ]

    real_write_checkpoint = supervisor_module._write_checkpoint
    calls = {"count": 0}

    def failing_write(path, payload):
        calls["count"] += 1
        if calls["count"] >= 3:
            raise supervisor_module.SupervisorError(
                "falha simulada",
                "CHECKPOINT_WRITE_FAILED",
            )
        return real_write_checkpoint(path, payload)

    monkeypatch.setattr(
        "evobyte.supervisor._write_checkpoint",
        failing_write,
    )

    with pytest.raises(supervisor_module.SupervisorError):
        run_supervised(
            command,
            make_budget(1.0),
            checkpoint,
            poll_interval_seconds=0.01,
            observation_interval_seconds=0.05,
            checkpoint_interval_seconds=0.2,
        )

    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline and not pid_path.exists():
        time.sleep(0.01)

    assert pid_path.exists()
    worker_pid = int(pid_path.read_text(encoding="utf-8"))
    assert wait_pid_gone(worker_pid)


def test_invalid_arguments_are_rejected(tmp_path):
    budget = make_budget(1.0)
    checkpoint = tmp_path / "checkpoint.json"

    with pytest.raises(SupervisorError) as exc:
        run_supervised("python -c pass", budget, checkpoint)
    assert exc.value.code == "INVALID_COMMAND"

    with pytest.raises(SupervisorError) as exc:
        run_supervised([], budget, checkpoint)
    assert exc.value.code == "INVALID_COMMAND"

    with pytest.raises(SupervisorError) as exc:
        run_supervised([sys.executable, "-c", "pass"], object(), checkpoint)
    assert exc.value.code == "INVALID_BUDGET"

    with pytest.raises(SupervisorError) as exc:
        run_supervised(
            [sys.executable, "-c", "pass"],
            budget,
            checkpoint,
            poll_interval_seconds=0,
        )
    assert exc.value.code == "INVALID_INTERVAL"

    with pytest.raises(SupervisorError) as exc:
        run_supervised(
            [sys.executable, "-c", "pass"],
            budget,
            checkpoint,
            kill_grace_seconds=-1,
        )
    assert exc.value.code == "INVALID_GRACE"

    with pytest.raises(SupervisorError) as exc:
        run_supervised(
            [sys.executable, "-c", "pass"],
            budget,
            checkpoint,
            preflight=1,
        )
    assert exc.value.code == "INVALID_PREFLIGHT"

    directory_checkpoint = tmp_path / "checkpoint-dir"
    directory_checkpoint.mkdir()
    with pytest.raises(SupervisorError) as exc:
        run_supervised(
            [sys.executable, "-c", "pass"],
            budget,
            directory_checkpoint,
        )
    assert exc.value.code == "INVALID_CHECKPOINT_PATH"
