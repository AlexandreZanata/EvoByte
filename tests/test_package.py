"""Testes do pacote mínimo evobyte (F01-T01)."""

import sys


def test_package_import():
    import evobyte

    assert hasattr(evobyte, "__version__")
    assert evobyte.__version__ == "0.1.0"


def test_no_heavy_frameworks_imported():
    import evobyte

    # Importar evobyte no nível base não deve carregar numpy ou torch
    assert "numpy" not in sys.modules, "evobyte não deve importar NumPy por padrão"
    assert "torch" not in sys.modules, "evobyte não deve importar PyTorch por padrão"
