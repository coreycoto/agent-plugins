"""Frozen scope assertion; diagnostic quality requires separate semantic grading."""
import runpy
from pathlib import Path

support = runpy.run_path(str(Path(__file__).resolve().parents[2] / "_readonly_oracle.py"))
support["main"](Path(__file__).resolve().parents[1] / "fixtures")
