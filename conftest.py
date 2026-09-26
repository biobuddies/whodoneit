"""Build fossil once for tests."""

from subprocess import check_call

check_call([
    'uv',
    'run',
    '--no-project',
    '--with=setuptools',
    'python',
    '-c',
    'import setup; setup.build_fossil()',
])
