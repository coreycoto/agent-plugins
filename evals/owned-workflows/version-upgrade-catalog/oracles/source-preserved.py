"""Frozen read-only scope assertion; semantic upgrade judgment uses a separate rubric."""
import runpy
from pathlib import Path

support = runpy.run_path(str(Path(__file__).resolve().parents[2] / "_readonly_oracle.py"))
support["main"](Path(__file__).resolve().parents[1] / "fixtures")
