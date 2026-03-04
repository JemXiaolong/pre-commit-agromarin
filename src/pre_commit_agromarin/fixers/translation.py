"""Fix prefer-env-translation: change _() to self.env._() in model methods."""

import re
from pathlib import Path


def fix_prefer_env_translation(filepath):
    """Replace standalone _() calls with self.env._() and clean unused imports.

    Returns True if the file was modified.
    """
    path = Path(filepath)
    if not path.exists():
        return False

    lines = path.read_text().splitlines(keepends=True)
    modified = False

    # Replace _( with self.env._(
    for i, line in enumerate(lines):
        new_line = re.sub(r'(?<![.\w])_\(', 'self.env._(', line)
        if new_line != line:
            lines[i] = new_line
            modified = True

    # Clean up unused _ import if no standalone _() calls remain
    if modified:
        content = ''.join(lines)
        if not re.search(r'(?<![.\w])_\(', content):
            _remove_underscore_import(lines)

    if modified:
        path.write_text(''.join(lines))

    return modified


def _remove_underscore_import(lines):
    """Remove unused _ import from lines (modifies in place)."""
    for i, line in enumerate(lines):
        # "from odoo.tools.translate import _"
        if re.match(r'^\s*from\s+odoo\.tools\.translate\s+import\s+_\s*$', line):
            del lines[i]
            if 0 < i < len(lines):
                if lines[i - 1].strip() == '' and lines[i].strip() == '':
                    del lines[i]
            return

        # "from odoo import _, api, ..."
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
                return
