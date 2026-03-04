"""Fix no-else-raise: remove unnecessary else after raise statements."""

import re
from pathlib import Path


def fix_no_else_raise(filepath):
    """Remove unnecessary else blocks after raise statements.

    Returns True if the file was modified.
    """
    path = Path(filepath)
    if not path.exists():
        return False

    lines = path.read_text().splitlines(keepends=True)
    modified = False
    i = 0

    while i < len(lines):
        match = re.match(r'^(\s*)else\s*:\s*$', lines[i])
        if not match:
            i += 1
            continue

        else_indent = len(match.group(1))

        # Check if the block before ends with a raise
        has_raise = False
        for j in range(i - 1, max(-1, i - 30), -1):
            stripped = lines[j].strip()
            if not stripped:
                continue
            if stripped.startswith('raise ') or stripped == 'raise':
                has_raise = True
                break
            line_indent = len(lines[j]) - len(lines[j].lstrip())
            if line_indent <= else_indent:
                break

        if not has_raise:
            i += 1
            continue

        # Delete else: line and de-indent body
        del lines[i]
        while i < len(lines):
            stripped = lines[i].strip()
            if not stripped:
                i += 1
                continue
            line_indent = len(lines[i]) - len(lines[i].lstrip())
            if line_indent <= else_indent:
                break
            lines[i] = lines[i][4:]
            i += 1

        modified = True

    if modified:
        path.write_text(''.join(lines))

    return modified
