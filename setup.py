from setuptools import find_packages, setup

setup(
    name="pre-commit-agromarin",
    version="2.0.0",
    description="AgroMarin pre-commit hooks for Odoo development",
    author="AgroMarin",
    license="LGPL-3.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "polib",
        "autoflake>=2.3",
        "pyupgrade>=3.19",
        "black>=24.0",
        "isort>=5.0",
        "flake8>=7.0",
        "flake8-bugbear",
    ],
    entry_points={
        "console_scripts": [
            "agromarin-fix=pre_commit_agromarin.cli:fix_main",
            "agromarin-check=pre_commit_agromarin.cli:check_main",
            "agromarin-po-format=pre_commit_agromarin.cli:po_format_main",
        ],
    },
    python_requires=">=3.10",
)
