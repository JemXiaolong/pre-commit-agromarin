from setuptools import find_packages, setup

setup(
    name="pre-commit-agromarin",
    version="1.0.0",
    description="AgroMarin pre-commit hooks for Odoo development",
    author="AgroMarin",
    license="LGPL-3.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["polib"],
    entry_points={
        "console_scripts": [
            "agromarin-po-format=pre_commit_agromarin.po_format:main",
            "agromarin-auto-fix=pre_commit_agromarin.auto_fix:main",
        ],
    },
    python_requires=">=3.10",
)
