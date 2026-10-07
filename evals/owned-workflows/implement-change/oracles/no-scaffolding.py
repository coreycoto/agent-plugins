"""Independent artifact assertion; not copied into the consumer workspace."""
import runpy
from pathlib import Path

support = runpy.run_path(str(Path(__file__).resolve().parents[2] / "_oracle_support.py"))
support["oracle_main"](__file__)
