"""CLI entry points for AgroMarin pre-commit hooks."""

import sys
from pathlib import Path

from .fixers import ALL_FIXERS
from .po_format import fix_file as fix_po_file


def custom_fixers_main():
    """Entry point for agromarin-custom-fixers hook.

    Runs Odoo-specific fixers that generic linters (ruff, pylint-odoo) do
    not cover:
        - prefer-env-translation: _() -> self.env._()
        - field-string-redundant: drop string= when it matches the
          auto-generated label

    Returns 1 if any file was modified, 0 otherwise.
    """
    files = [f for f in sys.argv[1:] if f.endswith(".py")]
    if not files:
        return 0

    before = {f: Path(f).read_bytes() for f in files if Path(f).exists()}

    for fixer in ALL_FIXERS:
        for filepath in files:
            fixer(filepath)

    after = {f: Path(f).read_bytes() for f in files if Path(f).exists()}
    modified = [f for f in files if before.get(f) != after.get(f)]

    if modified:
        sys.stderr.write(
            f"agromarin-custom-fixers modified {len(modified)} file(s):\n"
        )
        for f in modified:
            sys.stderr.write(f"  - {f}\n")
        return 1

    return 0


def po_format_main():
    """Entry point for agromarin-po-format hook.

    Formats .po files: sort by msgid, clear redundant translations.
    Returns 1 if any file was modified, 0 otherwise.
    """
    files = sys.argv[1:]
    ret = 0
    for filepath in files:
        if fix_po_file(filepath):
            ret = 1
    return ret
