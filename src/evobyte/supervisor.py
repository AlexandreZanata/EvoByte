"""Supervisão de um trabalhador em grupo de processos próprio.

O supervisor fica no processo pai, usa o relógio do ``Budget``, solicita stop,
TERM e KILL nos marcos, observa o grupo de processos e registra o resultado real.
Checkpoints são gravados atomicamente e o estado final é decidido pelo pai, não
por um timeout interno do trabalhador. Contrato em
docs/03-architecture-and-contracts.md e docs/05-experiment-budget.md.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
from typing import Any, Callable, Sequence

from .budget import Budget

COMPLETED = "completed"
TIMEOUT = "timeout"
CRASHED = "crashed"
OOM = "oom"
EXTERNAL_FAILURE = "external_failure"

RUN_STATUSES = frozenset({COMPLETED, TIMEOUT, CRASHED, OOM, EXTERNAL_FAILURE})

STOP_FILENAME = "stop.requested"
STDOUT_FILENAME = "worker.stdout.log"
STDERR_FILENAME = "worker.stderr.log"

DEFAULT_POLL_INTERVAL_SECONDS = 0.02
DEFAULT_OBSERVATION_INTERVAL_SECONDS = 0.1
DEFAULT_CHECKPOINT_INTERVAL_SECONDS = 5.0
DEFAULT_DESCENDANT_GRACE_SECONDS = 0.5


class SupervisorError(ValueError):
    """Erro estável de configuração ou operação do supervisor."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class RunResult:
    """Resultado observado pelo pai para uma execução supervisionada."""

    status: str
    exit_code: int | None
    signals: tuple[str, ...]
    reasons: tuple[str, ...]
    timed_out: bool
    t0: float
    wall_seconds: float
    overrun_seconds: float
    cpu_seconds: float | None
    max_rss_bytes: int | None
    descendants_seen: int | None
    worker_still_alive: bool
    process_group_empty: bool
    worker_pid: int | None
    pgid: int | None
    preflight_ok: bool | None
    checkpoints_written: int
    checkpoint_path: str
    stop_path: str
    stdout_path: str
    stderr_path: str
    started_at_utc: str
    finished_at_utc: str
    error: str | None
    gpu: None
    unavailable: dict[str, str]
    budget: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _is_finite_positive(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def _validate_command(command: Sequence[str]) -> list[str]:
    if isinstance(command, (str, bytes)) or not isinstance(command, Sequence):
        raise SupervisorError(
            "worker_command deve ser uma sequência de strings",
            "INVALID_COMMAND",
        )
    command_list = list(command)
    if not command_list or not all(isinstance(item, str) and item for item in command_list):
        raise SupervisorError(
            "worker_command deve ser não vazio e conter apenas strings",
            "INVALID_COMMAND",
        )
    return command_list


def _validate_interval(value: Any, name: str) -> float:
    if not _is_finite_positive(value):
        raise SupervisorError(f"{name} deve ser número finito > 0", "INVALID_INTERVAL")
    return float(value)


def _validate_grace(value: Any, name: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise SupervisorError(f"{name} deve ser número finito >= 0", "INVALID_GRACE")
    return float(value)


def _write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        ensure_ascii=False,
    ).encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=path.name + ".",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _write_checkpoint(path: Path, payload: Any) -> None:
    try:
        _write_json_atomic(path, payload)
    except OSError as exc:
        raise SupervisorError(
            f"falha ao gravar checkpoint: {exc}",
            "CHECKPOINT_WRITE_FAILED",
        ) from exc


def _read_proc_stat(pid: int) -> list[str] | None:
    try:
        data = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    try:
        return data.rsplit(")", 1)[1].split()
    except IndexError:
        return None


def _read_proc_cpu_seconds(pid: int) -> float | None:
    fields = _read_proc_stat(pid)
    if fields is None or len(fields) < 13:
        return None
    try:
        utime = int(fields[11])
        stime = int(fields[12])
        ticks = os.sysconf("SC_CLK_TCK")
    except (ValueError, OSError, AttributeError):
        return None
    if ticks <= 0:
        return None
    return (utime + stime) / ticks


def _read_proc_rss_bytes(pid: int) -> int | None:
    try:
        lines = Path(f"/proc/{pid}/status").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    for line in lines:
        if line.startswith("VmHWM:"):
            parts = line.split()
            if len(parts) >= 2:
                try:
                    return int(parts[1]) * 1024
                except ValueError:
                    return None
    return None


def _group_members(pgid: int) -> set[int] | None:
    proc = Path("/proc")
    if not proc.is_dir():
        return None
    try:
        entries = list(proc.iterdir())
    except OSError:
        return None

    members: set[int] = set()
    for entry in entries:
        if not entry.name.isdigit():
            continue
        fields = _read_proc_stat(int(entry.name))
        if fields is None or len(fields) < 13:
            continue
        try:
            if int(fields[2]) == pgid:
                members.add(int(entry.name))
        except ValueError:
            continue
    return members


def _group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _signal_group(pgid: int, signum: int) -> bool:
    try:
        os.killpg(pgid, signum)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def _wait4_nohang(pid: int) -> tuple[int | None, Any | None]:
    try:
        waited_pid, status, rusage = os.wait4(pid, os.WNOHANG)
    except ChildProcessError:
        return None, None
    if waited_pid == 0:
        return None, None
    try:
        return os.waitstatus_to_exitcode(status), rusage
    except ValueError:
        return None, None


def _wait_group_empty(pgid: int, timeout_seconds: float, poll_seconds: float) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if not _group_exists(pgid):
            return True
        time.sleep(poll_seconds)
    return not _group_exists(pgid)


def _base_unavailable() -> dict[str, str]:
    return {"gpu": "not_queried", "cuda": "not_queried"}


def _build_result(
    *,
    status: str,
    reasons: Sequence[str],
    signals: Sequence[str],
    checkpoint_path: Path,
    stop_path: Path,
    stdout_path: Path,
    stderr_path: Path,
    started_at_utc: str,
    preflight_ok: bool | None,
    checkpoints_written: int,
    budget: Budget,
    exit_code: int | None = None,
    leader_rusage: Any | None = None,
    descendant_cpu_seconds: float | None = None,
    max_rss_bytes: int | None = None,
    descendants_seen: int | None = None,
    worker_pid: int | None = None,
    pgid: int | None = None,
    worker_still_alive: bool = False,
    process_group_empty: bool = True,
    error: str | None = None,
    unavailable: dict[str, str] | None = None,
) -> RunResult:
    snapshot = budget.snapshot()
    unavailable_map = _base_unavailable()
    if unavailable:
        unavailable_map.update(unavailable)

    cpu_seconds: float | None
    if leader_rusage is None:
        cpu_seconds = None
        unavailable_map.setdefault("cpu_seconds", "worker_not_reaped")
    elif descendant_cpu_seconds is None:
        cpu_seconds = None
        unavailable_map.setdefault("cpu_seconds", "descendant_cpu_unavailable")
    else:
        cpu_seconds = leader_rusage.ru_utime + leader_rusage.ru_stime
        cpu_seconds += descendant_cpu_seconds

    if max_rss_bytes is None:
        unavailable_map.setdefault("max_rss_bytes", "not_observed")
    if descendants_seen is None:
        unavailable_map.setdefault("descendants_seen", "proc_unavailable")

    return RunResult(
        status=status,
        exit_code=exit_code,
        signals=tuple(signals),
        reasons=tuple(reasons),
        timed_out=status == TIMEOUT,
        t0=budget.t0,
        wall_seconds=snapshot["elapsed_seconds"],
        overrun_seconds=snapshot["overrun_seconds"],
        cpu_seconds=cpu_seconds,
        max_rss_bytes=max_rss_bytes,
        descendants_seen=descendants_seen,
        worker_still_alive=worker_still_alive,
        process_group_empty=process_group_empty,
        worker_pid=worker_pid,
        pgid=pgid,
        preflight_ok=preflight_ok,
        checkpoints_written=checkpoints_written,
        checkpoint_path=str(checkpoint_path),
        stop_path=str(stop_path),
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
        started_at_utc=started_at_utc,
        finished_at_utc=_utc_now(),
        error=error,
        gpu=None,
        unavailable=unavailable_map,
        budget=snapshot,
    )


def _finalize(
    result: RunResult,
    checkpoint_path: Path,
) -> RunResult:
    _write_checkpoint(checkpoint_path, result.to_dict())
    return result


def run_supervised(
    worker_command: Sequence[str],
    budget: Budget,
    checkpoint_path: str | Path,
    *,
    preflight: Callable[[], None] | None = None,
    poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS,
    observation_interval_seconds: float = DEFAULT_OBSERVATION_INTERVAL_SECONDS,
    checkpoint_interval_seconds: float = DEFAULT_CHECKPOINT_INTERVAL_SECONDS,
    descendant_grace_seconds: float = DEFAULT_DESCENDANT_GRACE_SECONDS,
    kill_grace_seconds: float | None = None,
) -> RunResult:
    """Executa e supervisiona o trabalhador, devolvendo o resultado do pai."""
    command = _validate_command(worker_command)
    if not isinstance(budget, Budget):
        raise SupervisorError("budget deve ser uma instância de Budget", "INVALID_BUDGET")
    poll_seconds = _validate_interval(poll_interval_seconds, "poll_interval_seconds")
    observation_seconds = _validate_interval(
        observation_interval_seconds,
        "observation_interval_seconds",
    )
    checkpoint_seconds = _validate_interval(
        checkpoint_interval_seconds,
        "checkpoint_interval_seconds",
    )
    descendant_grace = _validate_grace(
        descendant_grace_seconds,
        "descendant_grace_seconds",
    )
    if kill_grace_seconds is None:
        kill_grace = max(0.1, budget.limit_seconds - budget.kill_at_seconds)
    else:
        kill_grace = _validate_grace(kill_grace_seconds, "kill_grace_seconds")
    if preflight is not None and not callable(preflight):
        raise SupervisorError("preflight deve ser chamável", "INVALID_PREFLIGHT")

    checkpoint = Path(checkpoint_path)
    if checkpoint.exists() and checkpoint.is_dir():
        raise SupervisorError(
            "checkpoint_path não pode ser diretório",
            "INVALID_CHECKPOINT_PATH",
        )
    checkpoint.parent.mkdir(parents=True, exist_ok=True)

    stop_path = checkpoint.parent / STOP_FILENAME
    stdout_path = checkpoint.parent / STDOUT_FILENAME
    stderr_path = checkpoint.parent / STDERR_FILENAME
    started_at_utc = _utc_now()
    checkpoints_written = 0

    initial_snapshot = budget.snapshot()
    _write_checkpoint(
        checkpoint,
        {
            "status": "starting",
            "t0": budget.t0,
            "limit_seconds": budget.limit_seconds,
            "elapsed_seconds": initial_snapshot["elapsed_seconds"],
            "worker_pid": None,
            "pgid": None,
            "signals": [],
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "stop_path": str(stop_path),
            "budget": initial_snapshot,
        },
    )
    checkpoints_written += 1

    if budget.timed_out():
        result = _build_result(
            status=TIMEOUT,
            reasons=("BUDGET_EXHAUSTED_BEFORE_START",),
            signals=(),
            checkpoint_path=checkpoint,
            stop_path=stop_path,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            started_at_utc=started_at_utc,
            preflight_ok=None,
            checkpoints_written=checkpoints_written + 1,
            budget=budget,
        )
        return _finalize(result, checkpoint)

    preflight_ok: bool | None = None
    if preflight is not None:
        try:
            preflight()
        except Exception as exc:
            preflight_ok = False
            result = _build_result(
                status=EXTERNAL_FAILURE,
                reasons=("PREFLIGHT_FAILED",),
                signals=(),
                checkpoint_path=checkpoint,
                stop_path=stop_path,
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                started_at_utc=started_at_utc,
                preflight_ok=preflight_ok,
                checkpoints_written=checkpoints_written + 1,
                budget=budget,
                error=str(exc),
            )
            return _finalize(result, checkpoint)
        preflight_ok = True

    if budget.timed_out():
        result = _build_result(
            status=TIMEOUT,
            reasons=("BUDGET_EXHAUSTED_BEFORE_START",),
            signals=(),
            checkpoint_path=checkpoint,
            stop_path=stop_path,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            started_at_utc=started_at_utc,
            preflight_ok=preflight_ok,
            checkpoints_written=checkpoints_written + 1,
            budget=budget,
        )
        return _finalize(result, checkpoint)

    try:
        stdout_handle = open(stdout_path, "wb")
        stderr_handle = open(stderr_path, "wb")
    except OSError as exc:
        result = _build_result(
            status=EXTERNAL_FAILURE,
            reasons=("WORKER_LOG_UNAVAILABLE",),
            signals=(),
            checkpoint_path=checkpoint,
            stop_path=stop_path,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            started_at_utc=started_at_utc,
            preflight_ok=preflight_ok,
            checkpoints_written=checkpoints_written + 1,
            budget=budget,
            error=str(exc),
        )
        return _finalize(result, checkpoint)

    try:
        process = None
        worker_pid: int | None = None
        pgid: int | None = None
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=stdout_handle,
                stderr=stderr_handle,
                start_new_session=True,
            )
        except OSError as exc:
            result = _build_result(
                status=EXTERNAL_FAILURE,
                reasons=("WORKER_START_FAILED",),
                signals=(),
                checkpoint_path=checkpoint,
                stop_path=stop_path,
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                started_at_utc=started_at_utc,
                preflight_ok=preflight_ok,
                checkpoints_written=checkpoints_written + 1,
                budget=budget,
                error=str(exc),
            )
            return _finalize(result, checkpoint)

        worker_pid = process.pid
        pgid = worker_pid
        checkpoints_written += 1
        _write_checkpoint(
            checkpoint,
            {
                "status": "running",
                "t0": budget.t0,
                "limit_seconds": budget.limit_seconds,
                "worker_pid": worker_pid,
                "pgid": pgid,
                "elapsed_seconds": budget.snapshot()["elapsed_seconds"],
                "signals": [],
                "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path),
                "stop_path": str(stop_path),
            },
        )

        signals: list[str] = []
        reasons: list[str] = []
        stop_requested = False
        milestone_term = False
        milestone_kill = False
        cleanup_term = False
        cleanup_kill = False
        max_rss_bytes: int | None = None
        max_descendants = 0
        descendants_available = True
        leader_exit_code: int | None = None
        leader_rusage: Any | None = None
        worker_still_alive = False
        kill_deadline: float | None = None
        last_observation: float | None = None
        last_checkpoint = budget.elapsed_seconds()

        def observe() -> None:
            nonlocal max_rss_bytes, max_descendants, descendants_available
            members = _group_members(pgid)
            if members is None:
                descendants_available = False
                return
            descendants = {member for member in members if member != worker_pid}
            max_descendants = max(max_descendants, len(descendants))
            for member in members:
                rss = _read_proc_rss_bytes(member)
                if rss is not None:
                    max_rss_bytes = max(max_rss_bytes or 0, rss)

        def reap_if_exited() -> bool:
            nonlocal leader_exit_code, leader_rusage
            exit_code, rusage = _wait4_nohang(worker_pid)
            if exit_code is None:
                return False
            leader_exit_code = exit_code
            leader_rusage = rusage
            process.returncode = exit_code
            return True

        while True:
            if reap_if_exited():
                break

            elapsed = budget.elapsed_seconds()
            if last_observation is None or elapsed - last_observation >= observation_seconds:
                observe()
                last_observation = elapsed

            if not stop_requested and elapsed >= budget.search_stop_seconds:
                stop_requested = True
                try:
                    _write_json_atomic(
                        stop_path,
                        {"stop": True, "elapsed_seconds": elapsed},
                    )
                    signals.append("stop")
                except OSError:
                    reasons.append("STOP_REQUEST_FAILED")

            if not milestone_term and elapsed >= budget.terminate_at_seconds:
                if reap_if_exited():
                    break
                milestone_term = True
                if _signal_group(pgid, signal.SIGTERM):
                    signals.append("term")
                else:
                    reasons.append("TERM_SIGNAL_FAILED")

            if not milestone_kill and elapsed >= budget.kill_at_seconds:
                if reap_if_exited():
                    break
                milestone_kill = True
                if _signal_group(pgid, signal.SIGKILL):
                    signals.append("kill")
                else:
                    reasons.append("KILL_SIGNAL_FAILED")
                kill_deadline = time.monotonic() + kill_grace

            if elapsed >= budget.limit_seconds and not milestone_kill:
                if reap_if_exited():
                    break
                milestone_kill = True
                if _signal_group(pgid, signal.SIGKILL):
                    signals.append("kill")
                else:
                    reasons.append("KILL_SIGNAL_FAILED")
                kill_deadline = time.monotonic() + kill_grace

            if kill_deadline is not None and time.monotonic() >= kill_deadline:
                worker_still_alive = True
                reasons.append("WORKER_STILL_ALIVE")
                break

            if elapsed - last_checkpoint >= checkpoint_seconds:
                checkpoints_written += 1
                _write_checkpoint(
                    checkpoint,
                    {
                        "status": "running",
                        "t0": budget.t0,
                        "limit_seconds": budget.limit_seconds,
                        "worker_pid": worker_pid,
                        "pgid": pgid,
                        "elapsed_seconds": elapsed,
                        "signals": list(signals),
                        "max_rss_bytes": max_rss_bytes,
                        "descendants_seen": (
                            max_descendants if descendants_available else None
                        ),
                    },
                )
                last_checkpoint = elapsed

            time.sleep(poll_seconds)

        final_members = _group_members(pgid)
        if final_members is None:
            descendants_available = False
            group_present = _group_exists(pgid)
            orphan_members: set[int] = set()
        else:
            orphan_members = {
                member for member in final_members if member != worker_pid
            }
            max_descendants = max(max_descendants, len(orphan_members))
            group_present = bool(final_members) or _group_exists(pgid)

        descendant_cpu_seconds = 0.0
        descendant_cpu_complete = True
        for member in orphan_members:
            rss = _read_proc_rss_bytes(member)
            if rss is not None:
                max_rss_bytes = max(max_rss_bytes or 0, rss)
            member_cpu = _read_proc_cpu_seconds(member)
            if member_cpu is None:
                descendant_cpu_complete = False
            else:
                descendant_cpu_seconds += member_cpu

        orphans = bool(orphan_members)
        if (
            not orphans
            and leader_exit_code is not None
            and final_members is None
            and group_present
        ):
            orphans = True
        if orphans:
            reasons.append("ORPHAN_DESCENDANTS")

        if group_present:
            if not milestone_term and not cleanup_term:
                cleanup_term = True
                if _signal_group(pgid, signal.SIGTERM):
                    signals.append("term")
            if not _wait_group_empty(pgid, descendant_grace, poll_seconds):
                if not milestone_kill and not cleanup_kill:
                    cleanup_kill = True
                    if _signal_group(pgid, signal.SIGKILL):
                        signals.append("kill")
                if not _wait_group_empty(pgid, kill_grace, poll_seconds):
                    reasons.append("DESCENDANTS_STILL_ALIVE")

        process_group_empty = not _group_exists(pgid)
        if not process_group_empty:
            reasons.append("PROCESS_GROUP_NOT_EMPTY")

        if (
            worker_still_alive
            or milestone_term
            or milestone_kill
            or budget.timed_out()
        ):
            status = TIMEOUT
            if budget.timed_out() or budget.is_overrun():
                reasons.append("BUDGET_EXCEEDED")
        elif orphans or not process_group_empty:
            status = CRASHED
        elif leader_exit_code == 0:
            status = COMPLETED
        elif leader_exit_code is not None and leader_exit_code < 0:
            if (
                leader_exit_code == -signal.SIGKILL
                and not milestone_kill
                and not cleanup_kill
            ):
                status = OOM
                reasons.append("POSSIBLE_OOM")
            else:
                status = CRASHED
                reasons.append("SIGNAL_EXIT")
        else:
            status = CRASHED
            reasons.append("NONZERO_EXIT")

        if leader_rusage is None:
            descendant_cpu = None
        elif descendant_cpu_complete:
            descendant_cpu = descendant_cpu_seconds
        else:
            descendant_cpu = None

        result = _build_result(
            status=status,
            reasons=reasons,
            signals=signals,
            checkpoint_path=checkpoint,
            stop_path=stop_path,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            started_at_utc=started_at_utc,
            preflight_ok=preflight_ok,
            checkpoints_written=checkpoints_written + 1,
            budget=budget,
            exit_code=leader_exit_code,
            leader_rusage=leader_rusage,
            descendant_cpu_seconds=descendant_cpu,
            max_rss_bytes=max_rss_bytes,
            descendants_seen=max_descendants if descendants_available else None,
            worker_pid=worker_pid,
            pgid=pgid,
            worker_still_alive=worker_still_alive,
            process_group_empty=process_group_empty,
            unavailable=(
                {}
                if descendants_available
                else {"descendants_seen": "proc_unavailable"}
            ),
        )
        return _finalize(result, checkpoint)
    finally:
        if process is not None and process.returncode is None:
            if worker_pid is not None and pgid is not None:
                _signal_group(pgid, signal.SIGKILL)
                deadline = time.monotonic() + kill_grace
                while time.monotonic() < deadline:
                    try:
                        waited_pid, status, _ = os.wait4(worker_pid, os.WNOHANG)
                    except ChildProcessError:
                        break
                    if waited_pid != 0:
                        try:
                            process.returncode = os.waitstatus_to_exitcode(status)
                        except ValueError:
                            pass
                        break
                    time.sleep(poll_seconds)
                _wait_group_empty(pgid, kill_grace, poll_seconds)
        stdout_handle.close()
        stderr_handle.close()
