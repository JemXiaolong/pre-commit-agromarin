"""Fix field-string-redundant: remove redundant string= from field definitions."""

import re
from pathlib import Path


def fix_field_string_redundant(filepath):
    """Remove redundant string= parameters from Odoo field definitions.

    Returns True if the file was modified.
    """
    path = Path(filepath)
    if not path.exists():
        return False

    lines = path.read_text().splitlines(keepends=True)
    modified = False
    i = 0

    while i < len(lines):
        if not re.search(r'=\s*fields\.\w+\(', lines[i]):
            i += 1
            continue

        field_start, field_end = _find_field_block(lines, i)
        if field_start is None:
            i += 1
            continue

        if _remove_string_param(lines, field_start, field_end):
            modified = True
            continue

        i = field_end + 1 if field_end is not None else i + 1

    if modified:
        path.write_text(''.join(lines))

    return modified


def _find_field_block(lines, idx):
    """Find start and end of the field definition block containing idx."""
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


def _is_relational_field(line):
    """Check if the field definition is a relational field (comodel_name is required)."""
    relational = {"Many2one", "One2many", "Many2many", "Reference", "Many2oneReference"}
    match = re.search(r'fields\.(\w+)\(', line)
    return match is not None and match.group(1) in relational


def _remove_string_param(lines, field_start, field_end):
    """Remove string= parameter from a field block. Returns True if modified."""
    start_line = lines[field_start]

    # Never strip the first positional string from relational fields — it is
    # the comodel_name, not a redundant label.
    is_relational = _is_relational_field(start_line)

    # Positional string: fields.Integer("Sequence", default=10)
    if not is_relational and re.search(r'(fields\.\w+\()\s*(["\'])(.+?)\2\s*,', start_line):
        new_line = re.sub(
            r'(fields\.\w+\()\s*(["\'])(.+?)\2\s*,\s*', r'\1', start_line
        )
        if new_line != start_line:
            lines[field_start] = new_line
            return True

    # Positional string only: fields.XXX("String")
    if not is_relational and re.search(r'(fields\.\w+\()\s*(["\'])(.+?)\2\s*\)', start_line):
        new_line = re.sub(
            r'(fields\.\w+\()\s*(["\'])(.+?)\2\s*\)', r'\1)', start_line
        )
        if new_line != start_line:
            lines[field_start] = new_line
            return True

    # Keyword string= within the field block
    for check_idx in range(field_start, field_end + 1):
        check_line = lines[check_idx]
        if not re.search(r'\bstring\s*=\s*["\']', check_line):
            continue

        # Line contains ONLY string=
        if re.match(r'^\s+string\s*=\s*["\'].*["\']\s*,?\s*$', check_line):
            del lines[check_idx]
            return True

        # string= inline with other params
        new_line = re.sub(
            r',?\s*string\s*=\s*(["\']).*?\1\s*,?',
            lambda m: ','
            if m.group().startswith(',') and m.group().rstrip().endswith(',')
            else '',
            check_line,
        )
        new_line = re.sub(r',\s*\)', ')', new_line)
        new_line = re.sub(r'\(\s*,', '(', new_line)
        if new_line != check_line:
            lines[check_idx] = new_line
            return True

    return False
