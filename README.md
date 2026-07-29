# pre-commit-agromarin

Pre-commit hooks for AgroMarin Odoo development. Provides **Odoo-specific
fixers and formatters that no generic linter covers** (ruff, pylint-odoo).

Generic Python lints (unused imports, line length, modernization, ordering,
bugbear-style checks) are delegated to [ruff](https://github.com/astral-sh/ruff).
This repo no longer bundles black, isort, autoflake, pyupgrade, flake8, or
flake8-bugbear as of v3.0.0 — see the migration guide below.

## Hooks

### agromarin-custom-fixers

Auto-fix Odoo-specific conventions for Python files:

- **`prefer-env-translation`**: `_()` -> `self.env._()` in model methods.
  The env-scoped translation picks up module/record-language context correctly.
- **`field-string-redundant`**: drops `string="Speed"` when `field_name=speed`
  (Odoo auto-generates the same label from the field name).

### agromarin-po-format

Formats `.po` files:
- Sorts entries by `msgid`
- Clears redundant translations where `msgid == msgstr` (except `i18n_extra/`)

### agromarin-prettier

Formats XML and JavaScript files with Prettier 3.8.1 and
`@prettier/plugin-xml` 3.4.1.

### agromarin-eslint

Lints JavaScript files with ESLint 8.57.1 using the Odoo globals profile
in `config/.eslintrc.json`.

### agromarin-commit-format *(new in v3.1.0)*

Validates the commit message against the AgroMarin canonical format
(`core/doc/coding_guidelines.rst` §7.1):

- `[TAG] module: summary` — 13 allowed tags, first line ≤ 80 chars
- `module` accepts a single module, a comma-separated list for changes
  spanning several (`base, mail` / `sale,purchase,repair`), or the standalone
  wildcard `*` for tree-wide/generic changes (Odoo convention)
- Mandatory body ending with a `Task ID: XXXXX` footer
- Merge commits and `REL`/`MERGE` tags bypass the body requirement

Runs on the `commit-msg` stage — consumer repos must install that hook type:

```bash
pre-commit install --hook-type commit-msg
```

Previously this lived as a local script (`scripts/check_commit_msg.py`) in
agromarin-addons; hosting it here gives every repo (core, enterprise,
agromarin-addons) the same single-source validator.

## Usage

```yaml
repos:
  # Python linting/formatting via ruff
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.0
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format

  # Odoo-specific AgroMarin hooks
  - repo: https://github.com/JemXiaolong/pre-commit-agromarin
    rev: v3.1.0
    hooks:
      - id: agromarin-custom-fixers
      - id: agromarin-po-format
      - id: agromarin-prettier
      - id: agromarin-eslint
      - id: agromarin-commit-format
```

For upstream-code repos (core, enterprise) a minimal subset is recommended —
`agromarin-commit-format` plus ruff-check without `ruff-format` (never
whole-file reformat upstream code); skip the fixers/formatters.

A full reference configuration is available at
[`config/.pre-commit-config.yaml`](config/.pre-commit-config.yaml).

## Migration — v2.x → v3.0.0

**Breaking change**: the Python bundle (`agromarin-fix`, `agromarin-check`)
has been removed. Delegate to `ruff` in your consumer repo.

### What changed

| v2.x hook | v3.0.0 status | Replacement |
|-----------|---------------|-------------|
| `agromarin-fix` | **Removed** | `ruff-check --fix` + `ruff-format` (via `astral-sh/ruff-pre-commit`) |
| `agromarin-check` | **Removed** | `ruff-check` (bugbear rules are included) |
| *(inside `agromarin-fix`)* `no-else-raise` | **Removed** | ruff `RET506` |
| *(inside `agromarin-fix`)* `prefer-env-translation` | **Kept** | `agromarin-custom-fixers` (new name) |
| *(inside `agromarin-fix`)* `field-string-redundant` | **Kept** | `agromarin-custom-fixers` (new name) |
| `agromarin-po-format` | Unchanged | — |
| `agromarin-prettier` | Unchanged | — |
| `agromarin-eslint` | Unchanged | — |

### Steps for consumer repos

1. Add `astral-sh/ruff-pre-commit` to `.pre-commit-config.yaml` (see Usage
   above).
2. Replace `agromarin-fix` and `agromarin-check` hooks with
   `agromarin-custom-fixers`.
3. Bump `rev:` to `v3.0.0`.
4. Remove `[tool.black]` and `[tool.isort]` from `pyproject.toml`.
5. Create a `ruff.toml` (or extend the fork's `core/ruff.toml` if it exists).
6. Run `pre-commit clean && pre-commit install` to refresh hook envs.

### Why

- **Ruff replaces 5 tools** (autoflake/pyupgrade/black/isort/flake8+bugbear)
  with a single Rust binary — faster, better caching, fewer dependencies.
- **This package keeps what ruff cannot do**: Odoo-specific AgroMarin
  conventions (env-scoped translation, field-string redundancy), PO file
  formatting, Prettier with XML plugin, and ESLint with Odoo globals.

## Architecture

```
src/pre_commit_agromarin/
    cli.py              # Entry points (agromarin-custom-fixers, agromarin-po-format)
    check_commit_msg.py # Commit-message validator (agromarin-commit-format)
    po_format.py        # PO file formatter
    fixers/             # Custom AgroMarin fixers (modular)
        __init__.py     #   ALL_FIXERS list
        translation.py  #   prefer-env-translation
        field_string.py #   field-string-redundant
```

To add a new Odoo-specific fixer: create a module in `fixers/` with a
`fix_<name>(filepath) -> bool` function (returns True if modified), then
add it to `ALL_FIXERS` in `fixers/__init__.py`.

## Config Templates

The `config/` directory contains reference configurations for consumer repos:

- [`.pylintrc`](config/.pylintrc) — Pylint + pylint-odoo
- [`.eslintrc.json`](config/.eslintrc.json) — ESLint with Odoo globals
- [`.pre-commit-config.yaml`](config/.pre-commit-config.yaml) — Full reference
  pre-commit config (ruff + agromarin + OCA + file checks)

## License

LGPL-3.0
