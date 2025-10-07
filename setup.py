"""Setup script for Digital Footprint Analyzer"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="digital-footprint-analyzer",
    version="0.1.0",
    author="Digital Footprint Team",
    description="Analyze Gmail inboxes to create comprehensive digital persona reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/digital-footprint-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Email",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "google-auth>=2.25.0",
        "google-auth-oauthlib>=1.2.0",
        "google-auth-httplib2>=0.2.0",
        "google-api-python-client>=2.110.0",
        "google-generativeai>=0.3.2",
        "exa-py>=1.0.7",
        "apify-client>=1.5.0",
        "requests>=2.31.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "digital-footprint=src.main:main",
        ],
    },
)

