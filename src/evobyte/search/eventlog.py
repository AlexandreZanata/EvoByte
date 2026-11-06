"""Escrita incremental e limitada dos eventos da busca.

O motor entrega eventos por callback. Este módulo grava JSONL durante a busca,
limita o volume de eventos não-chave e preserva os eventos-chave. O fechamento
grava um resumo auditável; a lista completa de eventos não é acumulada em
memória nem despejada depois da busca.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any

EVENT_LOG_VERSION = 1
DEFAULT_KEY_EVENTS = frozenset(
    {
        "start",
        "new_best",
        "invalid_selector_stop",
        "invalid_action",
        "stop",
    }
)


class EventLogError(ValueError):
    """Erro estável de política ou de escrita do log de eventos."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


def _is_strict_int(value: Any) -> bool:
    return type(value) is int


@dataclass(frozen=True)
class EventLogPolicy:
    """Limites explícitos para o log incremental.

    ``max_non_key_events`` e ``max_bytes`` limitam somente eventos não-chave.
    Eventos-chave são sempre preservados; por isso o arquivo pode exceder
    ``max_bytes`` por uma pequena quantidade fixa.
    """

    max_non_key_events: int = 50_000
    max_bytes: int = 16 * 1024 * 1024
    flush_every: int = 128
    key_events: frozenset[str] = DEFAULT_KEY_EVENTS

    def __post_init__(self) -> None:
        if (
            not _is_strict_int(self.max_non_key_events)
            or self.max_non_key_events < 0
        ):
            raise EventLogError(
                "max_non_key_events deve ser inteiro estrito >= 0",
                "INVALID_MAX_EVENTS",
            )
        if not _is_strict_int(self.max_bytes) or self.max_bytes <= 0:
            raise EventLogError(
                "max_bytes deve ser inteiro estrito > 0",
                "INVALID_MAX_BYTES",
            )
        if not _is_strict_int(self.flush_every) or self.flush_every < 1:
            raise EventLogError(
                "flush_every deve ser inteiro estrito >= 1",
                "INVALID_FLUSH_INTERVAL",
            )
        if not isinstance(self.key_events, (set, frozenset)) or not all(
            isinstance(name, str) and name.strip() for name in self.key_events
        ):
            raise EventLogError(
                "key_events deve ser conjunto de strings não vazias",
                "INVALID_KEY_EVENTS",
            )
        object.__setattr__(self, "key_events", frozenset(self.key_events))

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_non_key_events": self.max_non_key_events,
            "max_bytes": self.max_bytes,
            "flush_every": self.flush_every,
            "key_events": sorted(self.key_events),
        }


class EventLogWriter:
    """Grava eventos JSONL incrementalmente, com limite e resumo final."""

    def __init__(
        self,
        path: str | Path,
        policy: EventLogPolicy | None = None,
    ) -> None:
        if policy is None:
            policy = EventLogPolicy()
        if not isinstance(policy, EventLogPolicy):
            raise EventLogError(
                "policy deve ser EventLogPolicy",
                "INVALID_POLICY",
            )

        self.path = Path(path)
        self.policy = policy
        if self.path.exists():
            raise EventLogError(
                f"arquivo de eventos já existe: {self.path}",
                "EVENT_LOG_EXISTS",
            )
        try:
            self._handle = self.path.open("xb")
        except OSError as exc:
            raise EventLogError(
                f"falha ao criar log de eventos: {exc}",
                "EVENT_LOG_OPEN_FAILED",
            ) from exc

        self._events_total = 0
        self._events_written = 0
        self._non_key_written = 0
        self._non_key_dropped = 0
        self._key_written = 0
        self._bytes_written = 0
        self._non_key_bytes = 0
        self._key_bytes = 0
        self._file_size = 0
        self._first_dropped_index: int | None = None
        self._last_dropped_index: int | None = None
        self._closed = False
        self._aborted: bool | None = None
        self._summary_written = False

    def _drop(self, index: int) -> None:
        self._non_key_dropped += 1
        if self._first_dropped_index is None:
            self._first_dropped_index = index
        self._last_dropped_index = index

    def emit(self, event: Mapping[str, Any]) -> bool:
        """Grava um evento; devolve ``False`` quando ele foi descartado."""
        if self._closed:
            raise EventLogError(
                "não é possível escrever após o fechamento",
                "EVENT_LOG_CLOSED",
            )
        if not isinstance(event, Mapping):
            raise EventLogError(
                "evento deve ser um mapping JSON",
                "INVALID_EVENT",
            )

        self._events_total += 1
        index = self._events_total
        name = event.get("event")
        is_key = isinstance(name, str) and name in self.policy.key_events

        if not is_key and (
            self._non_key_written >= self.policy.max_non_key_events
            or self._bytes_written >= self.policy.max_bytes
        ):
            self._drop(index)
            return False

        try:
            line = (
                json.dumps(
                    dict(event),
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                )
                + "\n"
            ).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise EventLogError(
                "evento não é serializável em JSON canônico",
                "INVALID_EVENT",
            ) from exc

        if not is_key and self._bytes_written + len(line) > self.policy.max_bytes:
            self._drop(index)
            return False

        previous_size = self._file_size
        try:
            self._handle.write(line)
            new_written = self._events_written + 1
            if is_key or new_written % self.policy.flush_every == 0:
                self._handle.flush()
        except OSError as exc:
            try:
                self._handle.seek(previous_size)
                self._handle.truncate()
            except OSError:
                pass
            raise EventLogError(
                f"falha ao gravar evento: {exc}",
                "EVENT_LOG_WRITE_FAILED",
            ) from exc

        self._events_written = new_written
        self._file_size = previous_size + len(line)
        self._bytes_written += len(line)
        if is_key:
            self._key_written += 1
            self._key_bytes += len(line)
        else:
            self._non_key_written += 1
            self._non_key_bytes += len(line)
        return True

    def stats(self) -> dict[str, Any]:
        """Contadores atuais; ``aborted`` só é definido após o fechamento."""
        return {
            "schema_version": EVENT_LOG_VERSION,
            "path": str(self.path),
            "policy": self.policy.to_dict(),
            "events_total": self._events_total,
            "events_written": self._events_written,
            "events_dropped": self._non_key_dropped,
            "non_key_written": self._non_key_written,
            "non_key_dropped": self._non_key_dropped,
            "key_written": self._key_written,
            "key_dropped": 0,
            "bytes_written": self._bytes_written,
            "non_key_bytes": self._non_key_bytes,
            "key_bytes": self._key_bytes,
            "truncated": self._non_key_dropped > 0,
            "first_dropped_index": self._first_dropped_index,
            "last_dropped_index": self._last_dropped_index,
            "closed": self._closed,
            "aborted": self._aborted,
            "summary_written": self._summary_written,
        }

    def close(self, *, aborted: bool = False) -> dict[str, Any]:
        """Fecha o arquivo e grava o resumo final; idempotente."""
        if not isinstance(aborted, bool):
            raise EventLogError(
                "aborted deve ser booleano",
                "INVALID_ABORTED",
            )
        if self._closed:
            return self.stats()

        summary = self.stats()
        summary["aborted"] = aborted
        summary["closed"] = True
        summary["summary_written"] = True
        summary_event = {"event": "log_summary", **summary}
        try:
            line = (
                json.dumps(
                    summary_event,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                )
                + "\n"
            ).encode("utf-8")
            self._handle.write(line)
            self._handle.flush()
            os.fsync(self._handle.fileno())
            self._handle.close()
        except OSError as exc:
            try:
                self._handle.close()
            except OSError:
                pass
            raise EventLogError(
                f"falha ao fechar log de eventos: {exc}",
                "EVENT_LOG_CLOSE_FAILED",
            ) from exc

        self._closed = True
        self._aborted = aborted
        self._summary_written = True
        return self.stats()

    def __enter__(self) -> "EventLogWriter":
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        self.close(aborted=exc_type is not None)
        return False
