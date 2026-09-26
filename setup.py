"""Build the fossil executable from the fossil-source submodule into the wheel's scripts."""

from pathlib import Path
from subprocess import check_call, check_output
from typing import override

from distutils.command.build_scripts import build_scripts
from setuptools import Distribution, setup
from setuptools.command.build import build
from setuptools.command.sdist import sdist

SOURCE = Path(__file__).with_name('fossil-source')
FOSSIL = Path(__file__).parent / 'build' / 'fossil'


def fetch_source() -> None:
    """Initialize the submodule unless present, as in sdists; actions/checkout omits it."""
    if not (SOURCE / 'configure').exists():
        check_call(['git', 'submodule', 'update', '--init', SOURCE.name], cwd=SOURCE.parent)  # noqa: S603


def build_fossil() -> None:
    """Configure and make fossil, skipping when build/fossil exists."""
    if FOSSIL.exists():
        return
    fetch_source()
    FOSSIL.parent.mkdir(exist_ok=True)
    check_call([SOURCE / 'configure', '--json'], cwd=FOSSIL.parent)  # noqa: S603
    check_call(['make'], cwd=FOSSIL.parent)


class Build(build):
    @override
    def run(self) -> None:
        build_fossil()
        super().run()


class Sdist(sdist):
    """Include submodule files, which setuptools_scm's git file finder skips."""

    @override
    def make_distribution(self) -> None:
        fetch_source()
        self.filelist.extend(
            f'{SOURCE.name}/{path}'
            for path in check_output(['git', 'ls-files'], cwd=SOURCE, text=True).splitlines()
        )
        super().make_distribution()


class BuildScripts(build_scripts):
    """Copy the binary verbatim; build_scripts would parse it for a Python shebang."""

    @override
    def run(self) -> None:
        self.mkpath(self.build_dir)
        self.copy_file(str(FOSSIL), self.build_dir)


class BinaryDistribution(Distribution):
    @override
    def has_ext_modules(self) -> bool:
        return True


if __name__ == '__main__':
    setup(
        cmdclass={'build': Build, 'build_scripts': BuildScripts, 'sdist': Sdist},  # pyrefly: ignore[bad-argument-type]
        distclass=BinaryDistribution,
        scripts=[str(FOSSIL.relative_to(Path(__file__).parent))],
    )
