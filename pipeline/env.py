"""Read settings from environment variables, falling back to a local .env file (never committed)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _dotenv():
    p = ROOT / ".env"
    vals = {}
    if p.exists():
        for line in p.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip()
    return vals


_DOT = _dotenv()


def get(name, default=None):
    return os.environ.get(name) or _DOT.get(name) or default
