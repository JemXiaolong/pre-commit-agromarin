"""isort wrapper - Python import sorter."""

import subprocess

DEFAULT_ARGS = ["--profile=black", "--line-length=88"]


def run(files, args=None):
    """Run isort on files. Returns exit code."""
    if not files:
        return 0
    cmd = ["isort"] + (args or DEFAULT_ARGS) + files
    return subprocess.call(cmd)
