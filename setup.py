#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="quads",
    version="1.0.1",
    description=("A pure Python Quadtree implementation."),
    author="Daniel Lindsley",
    author_email="daniel@toastdriven.com",
    url="http://github.com/toastdriven/quads",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    py_modules=["quads"],
    requires=[],
    install_requires=[],
    tests_require=["pytest",],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
