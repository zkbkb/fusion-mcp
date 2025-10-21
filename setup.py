from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fusion360_mcp_server",
    version="0.1.0",
    author="Fusion360 MCP Team",
    author_email="your.email@example.com",
    description="A Model Context Protocol server for Fusion 360 CAD automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fusion360-mcp-server",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: Apache-2.0 license",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: CAD",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp-python-sdk>=0.1.0",
        "pydantic>=2.0.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0",
        "websockets>=11.0.0",
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
            "pre-commit>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fusion360-mcp-server=fusion360_mcp_server.main:main",
        ],
    },
)
