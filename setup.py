# coding: utf-8

"""
Saskan Schema Admin and Services

:Contact: genuinemerit @ pm.me

Python3.9 (or whatever) must be installed.
See requirements.txt for notes on libraries to install using apt.

- git clone (or pull) git@github.com:genuinemerit/bow-data-schema.git
- git checkout **develop**
- `cd` __local/path/to/bow-data-schema__
- `python3.9 ./setup.py build`
- `sudo python3.9 ./setup.py install`
    - See notes in requirements.txt if problems doing component installs.
- `python3.9 install.py`

To make the program executable from command line `install.py` will:
- Copy shell script `..install/saskan_data` to HOME/.local/bin.
- Set up the .saskantinon directory under home dir.
- Copy resources and scripts into `~/saskantinon` dirs from git clone.

To rebuild the database, edit `~/saskantinon/log/db_status`,
  setting it to INCOMPLETE, then run `saskan_data`.
Note that the db_status file does not exist until the program
  has been run at least once.

To run the program:  type `saskan_data` at any command line.

"""
# IMPORTS
from setuptools import setup, find_packages   # type: ignore
# CONSTANTS
NAME = "BowDataSchema"
VERSION = "0.1.2"
with open('./requirements.txt', 'r') as f_req:
    REQUIRES = f_req.read()
with open('./README.md', 'r') as f_desc:
    README = f_desc.read()
# SETUP
setup(
    name=NAME,
    version=VERSION,
    author="Genuinemerit",
    author_email="genuinemerit@pm.me",
    description="Saskantinon Schema Editor and Services",
    long_description_content_type="text/markdown",
    long_description=README,
    url="https://github.com/genuinemerit/bow-data-schema.git",
    keywords=["BoW", "Saskan", "data", "services", "editor", "RPG"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: X11 Applications",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Platform :: Desktop",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Games/Entertainment"
    ],
    python_requires='>=3.9',
    project_urls={
        "Source": "https://github.com/genuinemerit/bow-data-schema.git",
        "Issues": "https://github.com/genuinemerit/bow-data-schema/issues",
        "Pull requests":
        "https://github.com/genuinemerit/bow-data-schema/pulls",
        "Project": "https://trello.com/bowax",
        "Technical Documentation": "https://github.com/genuinemerit/bow-wiki",
        "User Documentation": "https://github.com/genuinemerit/bow-wiki/wiki"
    }
)
