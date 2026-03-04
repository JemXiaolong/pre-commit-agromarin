"""Auto-fix common pylint-odoo lint patterns.

Receives Python file paths as arguments (standard pre-commit interface)
and applies deterministic fixes for:
- prefer-env-translation: _() -> self.env._()
- field-string-redundant: remove redundant string= parameter
- no-else-raise: remove unnecessary else after raise
"""

import re
import sys
from pathlib import Path


def _fix_prefer_env_translation(lines):
    """Replace standalone _() calls with self.env._() in all lines.

    Returns True if any modification was made.
    """
    modified = False
    for i, line in enumerate(lines):
        new_line = re.sub(r'(?<![.\w])_\(', 'self.env._(', line)
        if new_line != line:
            lines[i] = new_line
            modified = True
    return modified


def _remove_underscore_import(lines):
    """Remove unused _ import if no standalone _() calls remain.

    Returns True if any modification was made.
    """
    content = ''.join(lines)
    if re.search(r'(?<![.\w])_\(', content):
        return False  # _ is still used

    for i, line in enumerate(lines):
        # Pattern 1: "from odoo.tools.translate import _"
        if re.match(r'^\s*from\s+odoo\.tools\.translate\s+import\s+_\s*$', line):
            del lines[i]
            if 0 < i < len(lines):
                if lines[i - 1].strip() == '' and lines[i].strip() == '':
                    del lines[i]
            return True

        # Pattern 2: "from odoo import _, api, ..."
        match = re.match(r'^(\s*from\s+odoo\s+import\s+)(.*)', line)
        if match:
            prefix, imports_str = match.groups()
            imports = [
                x.strip()
                for x in imports_str.rstrip('\n').rstrip(',').split(',')
            ]
            if '_' in imports:
                imports.remove('_')
                lines[i] = prefix + ', '.join(imports) + '\n'
                return True

    return False


def _find_field_block(lines, idx):
    """Find the start and end of the field definition block containing idx.

    Returns (field_start, field_end) line indices, or (None, None).
    """
    field_start = None
    for i in range(idx, max(-1, idx - 12), -1):
        if re.search(r'=\s*fields\.\w+\(', lines[i]):
            field_start = i
            break

    if field_start is None:
        return None, None

    paren_depth = 0
    field_end = None
    for i in range(field_start, min(len(lines), field_start + 25)):
        for char in lines[i]:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
                if paren_depth == 0:
                    field_end = i
                    break
        if field_end is not None:
            break

    if field_end is None:
        field_end = min(len(lines) - 1, field_start + 12)

    return field_start, field_end


def _fix_field_string_redundant(lines):
    """Remove redundant string= parameters from field definitions.

    Scans all lines for field definitions and removes string= where present.
    Returns True if any modification was made.
    """
    modified = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if not re.search(r'=\s*fields\.\w+\(', line):
            i += 1
            continue

        field_start, field_end = _find_field_block(lines, i)
        if field_start is None:
            i += 1
            continue

        start_line = lines[field_start]

        # Positional string arg: fields.Integer("Sequence", default=10)
        pos_match = re.search(
            r'(fields\.\w+\()\s*(["\'])(.+?)\2\s*,', start_line
        )
        if pos_match:
            new_line = re.sub(
                r'(fields\.\w+\()\s*(["\'])(.+?)\2\s*,\s*',
                r'\1',
                start_line,
            )
            if new_line != start_line:
                lines[field_start] = new_line
                modified = True
                continue

        # Positional string only: fields.XXX("String")
        pos_only = re.search(
            r'(fields\.\w+\()\s*(["\'])(.+?)\2\s*\)', start_line
        )
        if pos_only:
            new_line = re.sub(
                r'(fields\.\w+\()\s*(["\'])(.+?)\2\s*\)',
                r'\1)',
                start_line,
            )
            if new_line != start_line:
                lines[field_start] = new_line
                modified = True
                continue

        # Keyword string= within the field block
        for check_idx in range(field_start, field_end + 1):
            check_line = lines[check_idx]
            if not re.search(r'\bstring\s*=\s*["\']', check_line):
                continue
            # Line contains ONLY string=
            if re.match(
                r'^\s+string\s*=\s*["\'].*["\']\s*,?\s*$', check_line
            ):
                del lines[check_idx]
                modified = True
                break
            # string= inline with other params
            new_line = re.sub(
                r',?\s*string\s*=\s*(["\']).*?\1\s*,?',
                lambda m: ','
                if m.group().startswith(',')
                and m.group().rstrip().endswith(',')
                else '',
                check_line,
            )
            new_line = re.sub(r',\s*\)', ')', new_line)
            new_line = re.sub(r'\(\s*,', '(', new_line)
            if new_line != check_line:
                lines[check_idx] = new_line
                modified = True
                break

        i = field_end + 1 if field_end is not None else i + 1

    return modified


def _fix_no_else_raise(lines):
    """Remove unnecessary else blocks after raise statements.

    Returns True if any modification was made.
    """
    modified = False
    i = 0
    while i < len(lines):
        line = lines[i]
        # Look for else: lines
        match = re.match(r'^(\s*)else\s*:\s*$', line)
        if not match:
            i += 1
            continue

        else_indent = len(match.group(1))

        # Check if the block before this else ends with a raise
        # by scanning backward for the if block
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

        # Delete the else: line
        del lines[i]

        # De-indent the else body (one level = 4 spaces)
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

    return modified


def fix_file(filepath):
    """Apply all auto-fixes to a single Python file.

    Returns True if the file was modified.
    """
    path = Path(filepath)
    if not path.exists():
        return False

    lines = path.read_text().splitlines(keepends=True)
    modified = False

    if _fix_prefer_env_translation(lines):
        modified = True
    if _fix_field_string_redundant(lines):
        modified = True
    if _fix_no_else_raise(lines):
        modified = True

    # Clean up unused _ imports after prefer-env-translation fix
    if modified and _remove_underscore_import(lines):
        pass  # already tracked as modified

    if modified:
        path.write_text(''.join(lines))
        print(f"  Fixed: {filepath}")

    return modified


def main(argv=None):
    """Entry point for pre-commit hook."""
    args = argv if argv is not None else sys.argv[1:]
    ret = 0
    for filepath in args:
        if fix_file(filepath):
            ret = 1
    return ret


if __name__ == "__main__":
    raise SystemExit(main())
