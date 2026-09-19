"""Vercel FastAPI entry. Same app as main.py; skip local cluster probes."""

from __future__ import annotations

import os

if not os.getenv("AERORESOLVE_KB") and not (os.getenv("DATABASE_URL") or "").strip():
    os.environ["AERORESOLVE_KB"] = "json"

from main import app  # noqa: F401
