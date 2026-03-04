"""Format .po files to match OCA expected format.

Sorts entries by msgid and clears redundant translations
(where msgid == msgstr), except in i18n_extra directories.
"""

import polib


def fix_file(filepath):
    """Reformat a single .po file. Returns True if modified."""
    try:
        po = polib.pofile(filepath)
    except Exception as exc:
        print(f"  Skipped: could not parse {filepath}: {exc}")
        return False

    original = str(po)

    po.sort(key=lambda entry: entry.msgid)

    if "/i18n_extra/" not in filepath:
        for entry in po:
            if entry.msgid == entry.msgstr:
                entry.msgstr = ""

    modified = str(po) != original
    if modified:
        po.save(filepath)
        print(f"  Fixed: {filepath}")

    return modified
