"""Configuración común para pruebas sin llamadas a proveedores externos."""
import os
import sys
import tempfile
import types
from pathlib import Path

_test_root = tempfile.TemporaryDirectory(prefix="aranza-tests-")
os.environ.setdefault("ARANZA_DB_PATH", str(Path(_test_root.name) / "test.sqlite3"))
os.environ.setdefault("ARANZA_PASSWORD", "test-password-123")
os.environ.setdefault("ARANZA_SESSION_SECRET", "test-secret-that-is-long-enough-for-unit-tests-123456")
os.environ.setdefault("ARANZA_ALLOWED_ORIGINS", "http://testserver")

if "groq" not in sys.modules:
    _groq = types.ModuleType("groq")
    class _UnusedAsyncGroq:
        def __init__(self, *args, **kwargs):
            pass
    _groq.AsyncGroq = _UnusedAsyncGroq
    sys.modules["groq"] = _groq
