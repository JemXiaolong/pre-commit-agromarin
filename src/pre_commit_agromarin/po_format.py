"""Format .po files to match OCA expected format.

Sorts entries by msgid and clears redundant translations
(where msgid == msgstr), except in i18n_extra directories.
"""

import sys

import polib


def fix_file(filepath):
    """Reformat a single .po file.

    Returns True if the file was modified.
    """
    try:
        po = polib.pofile(filepath)
    except Exception as exc:
        print(f"  Skipped: could not parse {filepath}: {exc}")
        return False

    original = str(po)

    po.sort(key=lambda entry: entry.msgid)

    # Clear translations where msgid == msgstr (same as OCA hook,
    # except for i18n_extra where identical translations are intentional)
    if "/i18n_extra/" not in filepath:
        for entry in po:
            if entry.msgid == entry.msgstr:
                entry.msgstr = ""

    modified = str(po) != original
    if modified:
        po.save(filepath)
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
