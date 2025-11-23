"""Setup script for Monopoly AI project."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="monopoly-ai",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A reproducible multi-agent Monopoly environment for RL research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/monopoly-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=[
        "numpy>=1.24.0",
        "pettingzoo>=1.24.0",
        "gymnasium>=0.29.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "rl": [
            "torch>=2.0.0",
            "stable-baselines3>=2.0.0",
        ],
        "analysis": [
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "pandas>=2.0.0",
        ],
    },
)
