from setuptools import setup, find_packages

setup(
    name="openweather_sdk",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    extras_require={
        "dev": ["pytest", "pytest-sugar"],
    },
    python_requires=">=3.8",
)