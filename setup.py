#!/usr/bin/env python3
"""
JPAPI - JAMF Pro API Toolkit
Distribution package with optional experimental UI features
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
readme_path = this_directory / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text()
else:
    long_description = "JAMF Pro API toolkit with optional experimental UI features"

setup(
    name="jpapi",
    version="1.1.0",
    author="JPAPI Contributors",
    author_email="maintainers@jpapi.dev",
    description="JAMF Pro API toolkit with optional experimental UI features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jpapi/jpapi",
    # Use py_modules since jpapi_main.py is now in src/
    py_modules=["src.jpapi_main"],
    packages=find_packages(where=".", include=["src*", "core*", "resources*"]),
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
    install_requires=[
        # Core dependencies - always required
        "requests>=2.25.0",
        "psutil>=5.8.0",
        "pandas>=1.3.0",
        "click>=8.0.0",
        "rich>=12.0.0",
        "keyring>=23.0.0",  # For credential storage
        "python-dateutil>=2.8.0",
        "pyjwt>=2.4.0",
    ],
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
    entry_points={
        "console_scripts": [
            "jpapi=src.jpapi_main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml"],
        "src": ["**/*"],
    },
    zip_safe=False,
    keywords=[
        "jamf",
        "mdm",
        "device-management",
        "api",
        "cli",
        "experimental-ui",
        "optional-features",
        "streamlit",
        "dash",
    ],
)
