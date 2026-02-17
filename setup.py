"""
Setup configuration for Project-AI.

This setup.py uses configuration from pyproject.toml.
For Python 3.11+, use: pip install -e .
"""

from setuptools import find_packages, setup

setup(
    packages=find_packages(where="."),
    package_dir={"": "."},
    entry_points={
        "console_scripts": [
            "project-ai=project_ai.main:main",
        ],
    },
)
