#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()


setup(
    name="Flask-OASSchema",
    version="0.9.14",
    url="https://github.com/IlyaSukhanov/flask-oasschema",
    license="MIT",
    author="Ilya Sukhanov",
    author_email="ilya@sukhanov.net",
    description="Flask extension for validating JSON requests",
    long_description=readme,
    py_modules=["flask_oasschema"],
    zip_safe=False,
    packages=["flask_oasschema"],
    platforms="any",
    install_requires=[
        "Flask>=0.9",
        "jsonschema>=1.1.0",
        "future>=0.16.0",
        "jsonref>=0.2",
    ],
    extras_require={
        "testing": [
            "flake8",
            "pytest",
            "pyflakes",
            "pytest-cov",
            "coverage",
            "wheel",
            "twine",
            "black",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
