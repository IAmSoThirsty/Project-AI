"""
Setup configuration for Project-AI.

This setup.py uses configuration from pyproject.toml.
For Python 3.11+, use: pip install -e .
"""

from setuptools import find_packages, setup

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "project-ai=app.main:main",
        ],
    },
)
