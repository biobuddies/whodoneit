"""Smoke test the fossil executable in the wheel from `mise build`."""

from pathlib import Path
from subprocess import check_output


def test_fossil_version() -> None:
    wheel = str(next(Path('dist').glob('*.whl')))
    assert check_output(['uvx', '--from', wheel, 'fossil', 'version']).startswith(b'This is ')
