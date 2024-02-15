# BibTeX Tools

[![PyPI - Version](https://img.shields.io/pypi/v/bibtextools)](https://pypi.org/project/bibtextools/)
[![Pytest](https://github.com/klb2/bibtex-tools/actions/workflows/pytest.yml/badge.svg)](https://github.com/klb2/bibtex-tools/actions/workflows/pytest.yml)
![GitHub License](https://img.shields.io/github/license/klb2/bibtex-tools)

This repository contains a collection of functions that might be helpful when
working with BibTeX files (`*.bib`).

The main purpose is to clean up bib files such that match the format for the
[biblatex](https://ctan.org/pkg/biblatex) package.

## Usage
Right now, the following functions are available

* [**Modernizing bib files:**](#modernizing-bib-files) `modernize`
* [**Cleaning bib files:**](#cleaning-bib-files) `clean`
* [**Combining bib files:**](#combining-bib-files) `combine`


Use `bibtex-tools --help` to list the possible commands and `bibtex-tools
<command> --help` to list the possible options for the sub-command `<command>`.


### Modernizing Bib Files
The command `bibtex-tools modernize` allows to update the format of several
fields in a bib-file.  This includes replacing the deprecated month strings
with the proper number entry, e.g., `month=jan` --> `month={1}`.  There also is
an option to download information from arXiv, if the `eprint` field is
available.

#### Example
If you want to add all relevant information from arXiv (with existing `eprint`
field) in your bib file `literature.bib`, you could use the following command
```bash
bibtex-tools modernize --arxiv literature.bib
```


### Cleaning Bib Files
The command `bibtex-tools clean` allows to clean a bib-files. This includes
replacing unicode characters by the LaTeX version.  It is also possible to pass
an additional file containing abbreviations, e.g., the `IEEEabbr.bib` file that
is often used by authors publishing in IEEE journals.

#### Example
If you want to remove the fields `abstract` and `isbn` from your bib file
`literature.bib`, you could use the following command
```bash
bibtex-tools clean -r abstract isbn literature.bib
```


### Combining Bib Files
The command `bibtex-tools combine` allows combining multiple bib-files into a
single one.  By default, it automatically renames duplicate entry IDs that
might occur after merging the files.

#### Example
If you want to combine the files `1.bib`, `2.bib`, and `3.bib` into a single
file called `literature.bib`, you can use the following command
```bash
bibtex-tools combine -o literature.bib 1.bib 2.bib 3.bib
```





## Installation
You can install the package from PyPI using
```bash
pip3 install bibtextools
```

You can also install the (possibly unstable) development version from the Git
repository using
```bash
git clone https://github.com/klb2/bibtex-tools
cd bibtex-tools
git checkout dev # if you want to checkout the development version
pip3 install . # you can use the -e option to track changes
```
