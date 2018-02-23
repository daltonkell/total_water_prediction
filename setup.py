import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

console_scripts = ['fleet = fleet.cli:main']
version = '0.1'
# requires =

setup(
    name = "fleet",
    version = version,
    author = "Dalton Kell",
    author_email = "dalton.kell@rpsgroup.com",
    description = ("A simple tool to launch and manage HPC fleets (clusters)."),
    packages = find_packages(),
    # install_requires = requires,
    entry_points=dict(console_scripts=console_scripts),
    include_package_data = True,
    zip_safe = False,
    package_data = {
        '' : ['examples/config'],
    },
    long_description=read('README.md'),
    # classifiers=[
    #     "Development Status :: 5 - Production/Stable",
    #     "Environment :: Console",
    #     "Programming Language :: Python",
    #     "Topic :: Scientific/Engineering",
    #     "License :: OSI Approved :: Apache Software License",
    # ],
)
