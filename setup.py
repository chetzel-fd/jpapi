#!/usr/bin/env python3
"""
JPAPI - JAMF Pro API Toolkit
Modular architecture with clean package structure
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
readme_path = this_directory / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text()
else:
    long_description = "JAMF Pro API toolkit with SOLID architecture"

setup(
    name="jpapi",
    version="2.0.0",
    author="JPAPI Contributors",
    author_email="maintainers@jpapi.dev",
    description="JAMF Pro API toolkit with modular architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chetzel-fd/jpapi",
    # Pure src/ layout - all packages are in src/
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    # Core dependencies - always required
    install_requires=[
        "requests>=2.25.0",
        "psutil>=5.8.0",
        "pandas>=1.3.0",
        "click>=8.0.0",
        "rich>=12.0.0",
        "keyring>=23.0.0",  # For credential storage
        "python-dateutil>=2.8.0",
        "pyjwt>=2.4.0",
    ],
    # Optional features
    extras_require={
        "ui": [
            # EXPERIMENTAL UI FEATURES - Optional and potentially unstable
            "streamlit>=1.20.0",
            "dash>=2.14.0",
            "plotly>=5.15.0",
            "dash-bootstrap-components>=1.5.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "enterprise": [
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.20.0",
            "pydantic>=2.0.0",
            "sqlalchemy>=2.0.0",
        ],
        "all": [
            # Install all optional features
            "streamlit>=1.20.0",
            "dash>=2.14.0",
            "plotly>=5.15.0",
            "dash-bootstrap-components>=1.5.0",
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.20.0",
            "pydantic>=2.0.0",
            "sqlalchemy>=2.0.0",
        ],
    },
    # Direct entry point (no path hacks needed)
    entry_points={
        "console_scripts": [
            "jpapi=jpapi_main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.md"],
    },
    zip_safe=False,
    keywords=[
        "jamf",
        "mdm",
        "device-management",
        "api",
        "cli",
        "solid-architecture",
    ],
)
