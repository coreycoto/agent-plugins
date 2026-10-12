"""Read-only artifact guard; semantic grading is separate."""
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("Usage: unchanged.py WORKSPACE RESPONSE_PATH EVENTS_PATH")
    workspace = Path(sys.argv[1]).resolve()
    files = {
        p.relative_to(workspace).as_posix()
        for p in workspace.rglob("*")
        if (p.is_file() or p.is_symlink())
        and p.relative_to(workspace).parts[0] != ".agents"
    }
    submitted = workspace / "review-scope.md"
    original = Path(__file__).resolve().parents[1] / "fixtures/review-scope.md"
    if (files != {"review-scope.md"} or submitted.is_symlink()
            or submitted.read_bytes() != original.read_bytes()):
        print("FAIL: review must leave product files unchanged.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
