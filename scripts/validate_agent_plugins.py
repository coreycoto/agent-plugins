#!/usr/bin/env python3
"""Validate publisher packages offline against the pinned Agent Plugins schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from author_checks.plugin_validation import validate_portable_plugin


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    schema = json.loads((args.repo_root / "schemas/agent-plugins-1.0.0.schema.json").read_text())
    errors = [error for root in sorted((args.repo_root / "plugins").iterdir())
              if root.is_dir() for error in validate_portable_plugin(root, schema)]
    for error in errors:
        print(error)
    if not errors:
        print("Agent Plugins 1.0.0 package validation passed.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
