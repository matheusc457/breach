from setuptools import setup, find_packages

setup(
    name="breach",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "rich>=13.0",
        "requests>=2.28",
        "beautifulsoup4>=4.12",
    ],
    entry_points={
        "console_scripts": [
            "breach=breach.cli:main",
        ],
    },
    python_requires=">=3.10",
    author="matheusc457",
    description="A terminal-based SCP Foundation database viewer.",
    url="https://github.com/matheusc457/breach",
)

