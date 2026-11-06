"""Tipos compartilhados pelos verificadores independentes.

Os verificadores de referência e de execução podem compartilhar apenas estes
tipos e a especificação de serialização, nunca o parser estrutural, a
adjacência ou o núcleo de detecção de ciclos.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Violation:
    """Violação estável com código e testemunho verificável."""

    code: str
    witness: tuple[Any, ...] | None = None


@dataclass(frozen=True)
class ValidationResult:
    """Resultado do contrato ``validate(raw_payload, expected_n)``."""

    valid: bool
    computed_m: int | None
    violations: tuple[Violation, ...]
    validator_id: str
    validator_version: str
    code_commit: str | None
    payload_sha256: str | None
