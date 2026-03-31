#                                           [2026-03-03 13:45]
#                                          Productivity: Out-Dated(archive)
"""
Thirstys Waterfall Setup
Production-grade integrated privacy-first system
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="thirstys-waterfall",
    version="1.0.0",
    author="Thirsty Security Team",
    author_email="security@thirstys.local",
    description="Integrated privacy-first system with 8 firewalls, built-in VPN, and incognito browser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IAmSoThirsty/Thirstys-waterfall",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: System :: Networking :: Firewalls",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=41.0.0",
    ],
    entry_points={
        "console_scripts": [
            "thirstys-waterfall=thirstys_waterfall.cli:main",
        ],
    },
)
