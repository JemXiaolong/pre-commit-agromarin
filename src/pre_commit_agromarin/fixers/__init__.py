"""Custom AgroMarin fixers for Odoo Python files.

Scope: Odoo-specific conventions that no generic linter (ruff, pylint-odoo)
enforces. Generic Python lints (unused imports, line length, modernization,
else-after-raise) are delegated to ruff in the consumer repository.
"""

from .field_string import fix_field_string_redundant
from .translation import fix_prefer_env_translation

ALL_FIXERS = [
    fix_prefer_env_translation,
    fix_field_string_redundant,
]
