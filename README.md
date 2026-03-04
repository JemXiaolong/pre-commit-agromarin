# pre-commit-agromarin

Pre-commit hooks for AgroMarin Odoo development. Bundles multiple tools into
a single CLI so consumer repos only need one `repo:` entry for all Python
linting and formatting.

## Hooks

### agromarin-fix

Auto-fix pipeline for Python files (runs in order):

1. **Custom fixers** (AgroMarin):
   - `prefer-env-translation`: `_()` -> `self.env._()`
   - `field-string-redundant`: removes redundant `string=`
   - `no-else-raise`: removes unnecessary `else` after `raise`
2. **autoflake**: removes unused imports
3. **pyupgrade**: modernizes Python syntax (3.12+)
4. **isort**: sorts imports (black profile)
5. **black**: formats code (line-length 88)

### agromarin-check

Lint check pipeline for Python files:
- **flake8** with **flake8-bugbear** plugin

### agromarin-po-format

Formats `.po` files:
- Sorts entries by `msgid`
- Clears redundant translations where `msgid == msgstr` (except `i18n_extra/`)

## Usage

```yaml
repos:
  - repo: https://github.com/JemXiaolong/pre-commit-agromarin
    rev: v2.0.0
    hooks:
      - id: agromarin-fix
      - id: agromarin-check
      - id: agromarin-po-format
```

This replaces separate entries for black, isort, autoflake, pyupgrade, and flake8.

## Architecture

```
src/pre_commit_agromarin/
    cli.py              # Entry points (agromarin-fix, agromarin-check, agromarin-po-format)
    runner.py           # Pipeline orchestrator
    po_format.py        # PO file formatter
    fixers/             # Custom AgroMarin fixers (modular)
        translation.py
        field_string.py
        no_else_raise.py
    tools/              # Third-party tool wrappers (modular)
        autoflake_tool.py
        pyupgrade_tool.py
        black_tool.py
        isort_tool.py
        flake8_tool.py
```

To add a new tool: create a module in `tools/` with a `run(files)` function,
then add it to the pipeline in `runner.py`.

## Config Templates

The `config/` directory contains reference configurations:
- `.pylintrc` - Pylint + pylint-odoo
- `.flake8` - Flake8
- `.eslintrc.json` - ESLint for Odoo JS
- `.pre-commit-config.yaml` - Full template for consumer repos

## License

LGPL-3.0
