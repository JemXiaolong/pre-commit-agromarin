"""Pyupgrade wrapper - modernizes Python syntax."""

import subprocess

DEFAULT_ARGS = ["--py312-plus"]


def run(files, args=None):
    """Run pyupgrade on files. Returns exit code."""
    if not files:
        return 0
    cmd = ["pyupgrade"] + (args or DEFAULT_ARGS) + files
    return subprocess.call(cmd)
