"""Whodoneit."""

from ctypes import CDLL, c_char_p
from pathlib import Path

libfossil = CDLL(Path(__file__).with_name('libfossil.so'))
libfossil.fsl_library_version.restype = c_char_p
