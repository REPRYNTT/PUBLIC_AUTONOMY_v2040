#!/usr/bin/env python3
"""
Setup script for Grokipedia Freedom Scraper
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="grokipedia-freedom-scraper",
    version="1.0.0",
    author="Freedom Scraper Team",
    author_email="freedom@example.com",
    description="Patriotic American-themed web scraper for Grokipedia knowledge extraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/grokipedia-freedom-scraper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=[
        "selenium>=4.0.0",
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "flask>=2.0.0",
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8"],
    },
    entry_points={
        "console_scripts": [
            "grokipedia-scraper=grokipedia_browser_scraper:main",
            "grokipedia-web=grokipedia_web_app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
