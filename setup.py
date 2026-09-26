"""Build the fossil executable from the fossil-source submodule into the wheel's scripts."""

from pathlib import Path
from subprocess import check_call, check_output
from typing import override

from distutils.command.build_scripts import build_scripts
from setuptools import setup
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.build import build
from setuptools.command.sdist import sdist

SOURCE = Path(__file__).with_name('fossil-source')
BUILD = Path(__file__).with_name('build')


class Build(build):
    @override
    def run(self) -> None:
        BUILD.mkdir(exist_ok=True)
        check_call([SOURCE / 'configure', '--json'], cwd=BUILD)  # noqa: S603
        check_call(['make'], cwd=BUILD)
        super().run()


class Sdist(sdist):
    """Include submodule files, which setuptools_scm's git file finder skips."""

    @override
    def make_distribution(self) -> None:
        self.filelist.extend(
            check_output(  # noqa: S603
                ['git', 'ls-files', '--recurse-submodules', SOURCE.name],
                cwd=SOURCE.parent,
                text=True,
            ).splitlines()
        )
        super().make_distribution()


class BuildScripts(build_scripts):
    """Copy the binary verbatim; build_scripts would parse it for a Python shebang."""

    @override
    def run(self) -> None:
        self.mkpath(self.build_dir)
        self.copy_file(str(BUILD / 'fossil'), self.build_dir)  # dup :scripts


class BdistWheel(bdist_wheel):
    """Tag py3-none-<platform>: fossil is native but needs no particular Python."""

    @override
    def finalize_options(self) -> None:
        super().finalize_options()
        self.root_is_pure = False

    @override
    def get_tag(self) -> tuple[str, str, str]:
        return 'py3', 'none', super().get_tag()[2]


if __name__ == '__main__':
    setup(
        cmdclass={  # pyrefly: ignore[bad-argument-type]
            'bdist_wheel': BdistWheel,
            'build': Build,
            'build_scripts': BuildScripts,
            'sdist': Sdist,
        },
        scripts=['build/fossil'],  # dup BuildScripts.run()
    )
