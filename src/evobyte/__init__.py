"""EvoByte: massively parallel evolutionary discovery via compact bytecode."""

from evobyte.cascade import CascadeConfig, CascadeStageCounters, StreamingGPUCascade
from evobyte.resident import GPUResidentEvolution

OPCODE_VERSION = 0

__version__ = "0.0.0"
__all__ = [
    "OPCODE_VERSION",
    "CascadeConfig",
    "CascadeStageCounters",
    "GPUResidentEvolution",
    "StreamingGPUCascade",
    "__version__",
]
