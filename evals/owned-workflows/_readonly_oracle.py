"""Preserve assessment inputs; independent of response wording or recommendations."""
import sys
from pathlib import Path


def main(fixtures):
    workspace = Path(sys.argv[1])
    expected = {p.relative_to(fixtures).as_posix(): p.read_bytes()
                for p in fixtures.rglob('*') if p.is_file()}
    try:
        actual = {}
        for path in workspace.rglob('*'):
            relative = path.relative_to(workspace)
            if relative.parts[0] == '.agents':
                continue  # The runtime checks exact procedure integrity separately.
            assert not path.is_symlink(), 'Unexpected symlink'
            if path.is_file() and '__pycache__' not in relative.parts:
                actual[relative.as_posix()] = path.read_bytes()
        assert actual == expected, 'Assessment changed the consumer files'
    except AssertionError as error:
        print('FAIL:', error)
        raise SystemExit(1) from None
    print('PASS: consumer unchanged')
