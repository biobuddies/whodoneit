from pathlib import Path
from subprocess import check_call

if not Path(__file__).with_name('libfossil.so').exists():
    check_call(['uv', 'run', '--no-project', '--with=setuptools', 'setup.py', 'build_libfossil'])
