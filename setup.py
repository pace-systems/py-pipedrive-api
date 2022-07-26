from os.path import exists

from setuptools import find_packages, setup

setup(
    name="py-pipedrive-api",
    author="Bill Schumacher",
    author_email="william.schumacher@gmail.com",
    packages=find_packages(),
    scripts=[],
    url="https://github.com/pace-systems/pipedrive-api",
    license="MIT",
    description="An unofficial Pipedrive API client.",
    long_description=open("README.md").read() if exists("README.md") else "",
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=[
        "requests",
    ],
    version="0.1.0",
    zip_safe=False,
)
