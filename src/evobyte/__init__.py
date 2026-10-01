"""EvoByte: massively parallel evolutionary discovery via compact bytecode."""

from evobyte.archive import EliteArchive, write_hall_of_fame_entry
from evobyte.cascade import CascadeConfig, CascadeStageCounters, StreamingGPUCascade
from evobyte.resident import GPUResidentEvolution
from evobyte.verifier import (
    L2VerificationResult,
    check_ordinary_math,
    check_symbolic_equivalence,
    export_reproducible_candidate,
    program_to_sympy,
    reproduce_candidate,
    verify_l2,
)
from evobyte.vm import execute_batch_f64, execute_f64

OPCODE_VERSION = 0

__version__ = "0.0.0"
__all__ = [
    "OPCODE_VERSION",
    "CascadeConfig",
    "CascadeStageCounters",
    "EliteArchive",
    "GPUResidentEvolution",
    "L2VerificationResult",
    "StreamingGPUCascade",
    "__version__",
    "check_ordinary_math",
    "check_symbolic_equivalence",
    "execute_batch_f64",
    "execute_f64",
    "export_reproducible_candidate",
    "program_to_sympy",
    "reproduce_candidate",
    "verify_l2",
    "write_hall_of_fame_entry",
]
