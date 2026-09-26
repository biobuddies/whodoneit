"""Build libfossil.so beside whodoneit.py; pyproject.toml holds everything else."""

from hashlib import sha256
from pathlib import Path
from shutil import copy2
from subprocess import check_call
from tarfile import open as open_tar
from tempfile import TemporaryDirectory
from urllib.request import urlopen

from setuptools import Command, Distribution, setup
from setuptools.command.build_py import build_py

CHECKIN = '1fcb8069dd445b4619119f2ab7e9a752e853d8ffbebea03cdcd06b1e32509958'
LIBRARY = Path(__file__).with_name('libfossil.so')


class BuildLibfossil(Command):
    """Download pinned libfossil source, verify, and `make dll` into the source tree."""

    user_options = []  # noqa: RUF012

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self) -> None:
        if LIBRARY.exists():
            return
        url = f'https://fossil.wanderinghorse.net/r/libfossil/tarball/{CHECKIN}/libfossil.tar.gz'
        with urlopen(url) as response, TemporaryDirectory() as directory:  # noqa: S310
            tarball = response.read()
            if sha256(tarball).hexdigest() != (
                'a5eb7a8b97190677742c126fc2b24bd80228450d335d6ea549ad9f9a4dccb750'
            ):
                raise ValueError(f'Unexpected sha256 for {url}')
            archive = Path(directory) / 'libfossil.tar.gz'
            archive.write_bytes(tarball)
            with open_tar(archive) as tar:
                tar.extractall(directory, filter='data')
            source = Path(directory) / 'libfossil'
            check_call(['./configure', '--disable-static'], cwd=source)
            check_call(['make', 'dll'], cwd=source)
            copy2(source / 'libfossil.so', LIBRARY)


class BuildPy(build_py):
    def run(self) -> None:
        self.run_command('build_libfossil')
        super().run()
        copy2(LIBRARY, Path(self.build_lib) / LIBRARY.name)


class BinaryDistribution(Distribution):
    def has_ext_modules(self) -> bool:
        return True


setup(
    cmdclass={'build_libfossil': BuildLibfossil, 'build_py': BuildPy},
    distclass=BinaryDistribution,
)
