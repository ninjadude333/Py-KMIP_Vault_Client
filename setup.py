# setup.py
from setuptools import setup, find_packages

setup(
    name="kmip_client",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "pymip==0.10.0",
        "configparser==5.3.0"
    ],
    python_requires=">=3.6",
)
