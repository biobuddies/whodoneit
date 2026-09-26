from whodoneit import libfossil


def test_libfossil_version() -> None:
    assert libfossil.fsl_library_version() == b'0.6.1'
