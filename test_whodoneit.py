"""Smoke test the fossil build."""

from subprocess import check_output


def test_fossil_version() -> None:
    assert check_output(['build/fossil', 'version']).startswith(b'This is fossil version 2.28 ')
