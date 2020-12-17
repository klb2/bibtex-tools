from setuptools import setup, find_packages

from digcommpy import __version__, __author__, __email__

with open("README.md") as rm:
    long_desc = rm.read()

with open("requirements.txt") as req:
    requirements = req.read().splitlines()

setup(
    name = "bibtextools",
    version = __version__,
    author = __author__,
    author_email = __email__,
    description = "Tools for working with BibTeX files",
    long_description=long_desc,
    license='GPLv3',
    url='https://gitlab.com/klb2/bibtex-tools',
    project_urls={
        #'Documentation': "https://digcommpy.readthedocs.io/",
        'Source Code': 'https://gitlab.com/klb2/bibtex-tools',
        },
    packages=find_packages(),
    tests_require=['pytest', 'tox'],
    install_requires=requirements,
)
