"""Autoflake wrapper - removes unused imports."""

import subprocess

DEFAULT_ARGS = [
    "--in-place",
    "--remove-all-unused-imports",
    "--ignore-init-module-imports",
]


def run(files, args=None):
    """Run autoflake on files. Returns exit code."""
    if not files:
        return 0
    cmd = ["autoflake"] + (args or DEFAULT_ARGS) + files
    return subprocess.call(cmd)
