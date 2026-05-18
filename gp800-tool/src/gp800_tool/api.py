"""GP800 API — selecteert automatisch FastAPI (64-bit) of Flask (32-bit).

64-bit met fastapi+uvicorn geinstalleerd  → api_fastapi.py
32-bit of geen fastapi                    → api_flask.py
"""
from pathlib import Path

def _use_fastapi() -> bool:
    """True als FastAPI beschikbaar en werkend is op dit systeem."""
    import struct
    if struct.calcsize("P") * 8 < 64:
        return False  # 32-bit: altijd Flask
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
        return True
    except ImportError:
        return False


if _use_fastapi():
    from .api_fastapi import create_app, serve  # noqa: F401
    _BACKEND = "FastAPI"
else:
    from .api_flask import create_app, serve  # noqa: F401
    _BACKEND = "Flask"

print(f"[GP800] API backend: {_BACKEND}")
