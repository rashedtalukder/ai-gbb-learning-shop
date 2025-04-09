"""
Setup script for the azure-sora-sdk package.
"""

from setuptools import setup, find_packages

setup(
    name="rashed_sora_sdk",
    version="0.1.0",
    author="Rashed Talukder",
    description="Azure OpenAI Sora Video Generation SDK",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "aiohttp>=3.8.0",
    ],
)
