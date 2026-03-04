"""Custom AgroMarin fixers for Odoo Python files."""

from .field_string import fix_field_string_redundant
from .no_else_raise import fix_no_else_raise
from .translation import fix_prefer_env_translation

ALL_FIXERS = [
    fix_prefer_env_translation,
    fix_field_string_redundant,
    fix_no_else_raise,
]
