# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / setup.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / setup.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""Setup configuration for Thirsty's Monolith."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="thirstys-monolith",
    version="1.0.0",
    author="Thirstys-Hub",
    description="Strict Enforcer for Repository Integrity - Schematic Guardian",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IAmSoThirsty/Thirstys-Monolith",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
)
