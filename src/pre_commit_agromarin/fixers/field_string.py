"""Fix field-string-redundant: remove redundant string= from field definitions.

A string= (or positional string) is redundant when its value exactly matches
the label Odoo would auto-generate from the field name via:

    field_name.replace("_", " ").title()

Examples:
  speed = fields.Float(string="Speed")          # redundant  → remove
  speed_limit = fields.Float(string="Speed Limit")  # redundant  → remove
  speed_limit = fields.Float(string="Speed (km/h)")  # meaningful → keep
  battery_threshold = fields.Float(string="Battery Threshold (%)")  # meaningful → keep
"""

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


def _get_field_name(line: str) -> str | None:
    """Extract the Python attribute name from a field declaration line.

    Example: '    speed_limit_warning = fields.Float(' → 'speed_limit_warning'
    """
    match = re.match(r'\s*(\w+)\s*=\s*fields\.\w+\(', line)
    return match.group(1) if match else None


def _auto_label(field_name: str) -> str:
    """Return the label Odoo auto-generates from a field name."""
    return field_name.replace("_", " ").title()


def _extract_string_value(text: str) -> str | None:
    """Extract the inner string value from the first quoted literal in *text*."""
    match = re.search(r'["\'](.+?)["\']', text)
    return match.group(1) if match else None


def _is_redundant(field_name: str | None, string_value: str | None) -> bool:
    """Return True only when the string equals Odoo's auto-generated label."""
    if field_name is None or string_value is None:
        return False
    return string_value == _auto_label(field_name)


def _remove_string_param(lines, field_start, field_end):
    """Remove string= parameter from a field block only when redundant.

    Returns True if modified.
    """
    start_line = lines[field_start]

    # Never strip the first positional string from relational fields — it is
    # the comodel_name, not a redundant label.
    is_relational = _is_relational_field(start_line)

    field_name = _get_field_name(start_line)

    # Positional string: fields.Integer("Sequence", default=10)
    pos_with_comma = re.search(r'(fields\.\w+\()\s*(["\'])(.+?)\2\s*,', start_line)
    if not is_relational and pos_with_comma:
        string_value = pos_with_comma.group(3)
        if _is_redundant(field_name, string_value):
            new_line = re.sub(
                r'(fields\.\w+\()\s*(["\'])(.+?)\2\s*,\s*', r'\1', start_line
            )
            if new_line != start_line:
                lines[field_start] = new_line
                return True

    # Positional string only: fields.XXX("String")
    pos_only = re.search(r'(fields\.\w+\()\s*(["\'])(.+?)\2\s*\)', start_line)
    if not is_relational and pos_only:
        string_value = pos_only.group(3)
        if _is_redundant(field_name, string_value):
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

        string_value = _extract_string_value(
            re.search(r'\bstring\s*=\s*(["\'].+?["\'])', check_line).group(1)
            if re.search(r'\bstring\s*=\s*(["\'].+?["\'])', check_line)
            else ""
        )

        if not _is_redundant(field_name, string_value):
            # String is meaningful — leave it alone
            return False

        # Line contains ONLY string= (and it is redundant)
        if re.match(r'^\s+string\s*=\s*["\'].*["\']\s*,?\s*$', check_line):
            del lines[check_idx]
            return True

        # string= inline with other params (and it is redundant)
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
