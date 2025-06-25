#!/usr/bin/env python3

from setuptools import find_packages, setup


# Read version from __init__.py
def get_version():
    with open("src/basic_open_agent_tools/__init__.py") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip("\"'")
    raise RuntimeError("Version not found")


# Read long description from README
def get_long_description():
    with open("README.md", encoding="utf-8") as f:
        return f.read()


setup(
    name="basic-open-agent-tools",
    version=get_version(),
    description="An open foundational toolkit providing essential components for building AI agents with minimal dependencies for local (non-HTTP/API) actions.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Open Agent Tools",
    author_email="unseriousai@gmail.com",
    url="https://github.com/open-agent-tools/basic-open-agent-tools",
    project_urls={
        "Homepage": "https://github.com/open-agent-tools/basic-open-agent-tools",
        "Documentation": "https://github.com/open-agent-tools/basic-open-agent-tools#readme",
        "Repository": "https://github.com/open-agent-tools/basic-open-agent-tools",
        "Issues": "https://github.com/open-agent-tools/basic-open-agent-tools/issues",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    keywords=["ai", "agents", "toolkit", "automation", "local-tools"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
)
