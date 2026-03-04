# pre-commit-agromarin

Pre-commit hooks for AgroMarin Odoo development.

## Hooks

### agromarin-po-format

Formats `.po` files to match OCA expected format:
- Sorts entries by `msgid`
- Clears redundant translations where `msgid == msgstr` (except `i18n_extra/`)

### agromarin-auto-fix

Auto-fixes common pylint-odoo patterns in Python files:
- `prefer-env-translation`: Replaces `_()` with `self.env._()`
- `field-string-redundant`: Removes redundant `string=` parameter from field definitions
- `no-else-raise`: Removes unnecessary `else` after `raise`
- Cleans up unused `_` imports after translation fixes

## Usage

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/JemXiaolong/pre-commit-agromarin
    rev: v1.0.0
    hooks:
      - id: agromarin-po-format
      - id: agromarin-auto-fix
```

## Config Templates

The `config/` directory contains reference configurations used across AgroMarin repos:
- `.pylintrc` - Pylint + pylint-odoo configuration
- `.flake8` - Flake8 configuration
- `.eslintrc.json` - ESLint configuration for Odoo JS
- `.pre-commit-config.yaml` - Full pre-commit template

Copy them to your repo root as needed.

## License

LGPL-3.0
