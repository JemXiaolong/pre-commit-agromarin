"""Flake8 wrapper - Python linter (includes bugbear plugin)."""

import subprocess


def run(files, args=None):
    """Run flake8 on files. Returns exit code."""
    if not files:
        return 0
    cmd = ["flake8"] + (args or []) + files
    return subprocess.call(cmd)
