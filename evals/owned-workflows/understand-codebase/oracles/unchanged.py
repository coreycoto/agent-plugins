import runpy
from pathlib import Path

suite = Path(__file__).resolve().parents[1]
runpy.run_path(str(suite.parent / "_readonly_oracle.py"))["main"](suite / "fixtures")
