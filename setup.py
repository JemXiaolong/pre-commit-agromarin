from setuptools import find_packages, setup

setup(
    name="pre-commit-agromarin",
    version="3.0.0",
    description=(
        "AgroMarin pre-commit hooks for Odoo development: "
        "custom Odoo-specific fixers + PO/prettier/eslint formatters. "
        "Generic Python linting is delegated to ruff."
    ),
    author="AgroMarin",
    license="LGPL-3.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "polib",
    ],
    entry_points={
        "console_scripts": [
            "agromarin-custom-fixers=pre_commit_agromarin.cli:custom_fixers_main",
            "agromarin-po-format=pre_commit_agromarin.cli:po_format_main",
        ],
    },
    python_requires=">=3.10",
)
