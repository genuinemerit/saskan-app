# coding: utf-8

"""
Saskantinon Applications - Game and Admin Tools

:Contact: genuinemerit @ pm.me

To get the software:
- git clone (or pull) git@github.com:genuinemerit/saskan-app.git
- develop is the default branch

To do a local install...
- Python3.10 (or whatever) must be installed.
- Creating a conda environment first is required.
- See notes in saskan.yml for details for what
  libraries to install using apt or pip.
- Activate the saskan environment before running saskan_install
- Edit config/d_dirs.json to identify where to put game dirs

Then...
- `cd [path-to]saskan_app`
- sudo ./saskan_intall  (a bash script that executes saskan_install.py)

To make the program executable from command line `saskan_install.py` will:
- Copy shell scripts to /usr/local/bin.
- Set up a `saskan` directory under the home dir.
- Copy resources and scripts into `~/saskan` dirs from the git clone.
- Set up and pickle temp resources into `/dev/shm/saskan`

To run the admin program:  type `saskan_admin` at any command line.
To run the game program: type `saskantinon` at any command line.`

To do a traditional packagead install, try something like this...
- `python ./setup.py build`
- `sudo python ./setup.py install`
Not sure if I have it set up right.
"""
# IMPORTS
from setuptools import setup, find_packages   # type: ignore
# CONSTANTS
NAME = "Saskantinon"
VERSION = "0.1.0"
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
    description="Saskantinon Game and Admin Tools",
    long_description_content_type="text/markdown",
    long_description=README,
    url="https://github.com/genuinemerit/saskan-app.git",
    keywords=["Saskantinon", "game", "editor", "RPG"],
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
        "Programming Language :: Python :: 3.10",
        "Topic :: Games/Entertainment"
    ],
    python_requires='>=3.9',
    project_urls={
        "Source": "https://github.com/genuinemerit/saskan-app.git",
        "Issues": "https://github.com/genuinemerit/saskan-app/issues",
        "Pull requests":
        "https://github.com/genuinemerit/saskan-app/pulls",
        "Documentation": "https://github.com/genuinemerit/saskan-wiki"
    }
)
