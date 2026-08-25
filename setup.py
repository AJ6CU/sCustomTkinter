# setup.py
from setuptools import setup, find_packages

setup(
    name="scustomtkinter",
    version="1.0.0",
    author="aj6cu",
    description="A theme-compliant custom widget library wrapping CustomTkinter.",
    url="https://github.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "scustomtkinter": ["assets/*.json"],
    },
    install_packages=[
        "customtkinter",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
