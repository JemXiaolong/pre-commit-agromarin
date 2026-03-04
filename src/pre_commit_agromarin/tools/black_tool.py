"""Black wrapper - Python code formatter."""

import subprocess

DEFAULT_ARGS = ["--line-length=88", "--quiet"]


def run(files, args=None):
    """Run black on files. Returns exit code."""
    if not files:
        return 0
    cmd = ["black"] + (args or DEFAULT_ARGS) + files
    return subprocess.call(cmd)
