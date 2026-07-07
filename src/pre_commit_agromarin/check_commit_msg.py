"""Validate commit message against AgroMarin canonical format.

Enforces the rules defined in the canonical coding guidelines
(``core/doc/coding_guidelines.rst``), section 7.1 Commit Messages:

- First line: ``[TAG] module: description``
- Max 80 characters on the first line
- One of 13 allowed tags: FIX, IMP, ADD, REM, REF, MOV, REV, REL, MERGE,
  I18N, PERF, CLN, LINT
- ``module`` is snake_case, optionally with ``/`` or ``.`` separators for
  sub-paths (e.g. ``account_cfdi``, ``stock/routes``)
- Body is mandatory and must end with a ``Task ID: XXXXX`` line

Exposed as the ``agromarin-commit-format`` hook (``commit-msg`` stage):
pre-commit invokes the console script with the commit-msg file path as the
single positional argument.
"""

from __future__ import annotations

import pathlib
import re
import sys

ALLOWED_TAGS = (
    "FIX",
    "IMP",
    "ADD",
    "REM",
    "REF",
    "MOV",
    "REV",
    "REL",
    "MERGE",
    "I18N",
    "PERF",
    "CLN",
    "LINT",
)
MAX_HEADER = 80
HEADER_RE = re.compile(
    rf"^\[(?P<tag>{'|'.join(ALLOWED_TAGS)})\] "
    r"(?P<module>[a-z][a-z0-9_]*(?:[/.][a-z][a-z0-9_]*)*): "
    r"(?P<summary>.+)$"
)
TASK_ID_RE = re.compile(r"^Task ID: \d{3,}$", re.MULTILINE)


def _fail(message: str) -> None:
    """Print a diagnostic and exit with status 1."""
    sys.stderr.write(f"\n❌ Commit message rejected: {message}\n\n")
    sys.stderr.write(
        "Expected format (canonical §7.1):\n"
        "    [TAG] module: short summary (<= 80 chars)\n\n"
        "    Problem / context sentence.\n\n"
        "    Solution:\n"
        "    - point 1\n"
        "    - point 2\n\n"
        "    Task ID: XXXXX\n\n"
        f"Allowed tags: {', '.join(ALLOWED_TAGS)}\n"
    )
    sys.exit(1)


def main(path: str) -> None:
    """Validate the commit message at *path*."""
    with pathlib.Path(path).open(encoding="utf-8") as f:
        content = f.read()

    # Strip trailing empty lines and comments that git adds
    lines = [line for line in content.splitlines() if not line.startswith("#")]
    if not lines:
        _fail("empty commit message")

    header = lines[0]

    # Auto-generated merge commits: allow git's default "Merge ..." format
    if header.startswith("Merge "):
        return

    if len(header) > MAX_HEADER:
        _fail(f"first line is {len(header)} chars (max {MAX_HEADER})")

    if not HEADER_RE.match(header):
        _fail(f"first line does not match [TAG] module: summary\n   Got: {header!r}")

    # Body + Task ID check (not required for REL or MERGE tags)
    tag = HEADER_RE.match(header).group("tag")
    if tag in {"REL", "MERGE"}:
        return

    body = "\n".join(lines[1:]).strip()
    if not body:
        _fail(
            "commit body is empty — canonical §7.1 requires Problem + Solution + Task ID"
        )

    if not TASK_ID_RE.search(body):
        _fail("commit body must end with 'Task ID: XXXXX' (canonical §7.3)")


def main_cli() -> int:
    """Console-script entry point for the ``agromarin-commit-format`` hook."""
    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} <commit-msg-file>\n")
        return 2
    main(sys.argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main_cli())
