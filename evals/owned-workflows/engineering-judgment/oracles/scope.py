"""Check read-only scope; design judgment uses a separate semantic rubric."""
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[2] / "_engineering_oracle.py"
spec = importlib.util.spec_from_file_location("engineering_oracle", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
raise SystemExit(module.main(Path(__file__).resolve().parents[1], "artifacts"))
