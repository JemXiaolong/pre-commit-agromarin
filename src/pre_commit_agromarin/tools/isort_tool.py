"""isort wrapper - Python import sorter.

isort reads configuration from the project's pyproject.toml, .isort.cfg,
or setup.cfg automatically. We avoid passing hardcoded args that would
override project-level settings (known_odoo, sections, etc.).
"""

import subprocess


def run(files, args=None):
    """Run isort on files. Returns exit code."""
    if not files:
        return 0
    cmd = ["isort"] + (args or []) + files
    return subprocess.call(cmd)
