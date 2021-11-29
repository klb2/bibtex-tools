# BibTeX Tools

[![PyPI version](https://badge.fury.io/py/bibtextools.svg)](https://badge.fury.io/py/bibtextools)
[![Gitlab Pipeline](https://gitlab.com/klb2/bibtex-tools/badges/master/pipeline.svg)](https://gitlab.com/klb2/bibtex-tools/-/pipelines)

This repository contains a collection of functions that might be helpful when
working with BibTeX files (`*.bib`).

The main purpose is to clean up bib files such that match the format for the
[biblatex](https://ctan.org/pkg/biblatex) package.

Right now, the following functions are available

* **Cleaning bib files:** The command `bibtex-tools clean` allows to clean a
  bib-files. This includes replacing unicode characters by the LaTeX version.
  It is also possible to pass an additional file containing abbreviations,
  e.g., the `IEEEabbr.bib` file that is often used by authors publishing in
  IEEE journals.
* **Modernizing bib files:** The command `bibtex-tools modernize` allows to
  update the format of several fields in a bib-file.
  This includes replacing the deprecated month strings with the proper number
  entry, e.g., `month=jan` --> `month={1}`.
  There also is an option to download information from arXiv, if the `eprint`
  field is available.
* **Combining bib files:** The command `bibtex-tools combine` allows combining
  multiple bib-files into a single one.
  By default, it automatically renames duplicate entry IDs that might occur
  after merging the files.

Use `bibtex-tools --help` to list the possible commands and `bibtex-tools
<command> --help` to list the possible options for the sub-command `<command>`.


## Installation
You can install the package from PyPI using
```bash
pip3 install bibtextools
```

You can also install the (possibly unstable) development version from the Git
repository using
```bash
git clone https://gitlab.com/klb2/bibtex-tools
cd bibtex-tools
git checkout dev # if you want to checkout the development version
pip3 install . # you can use the -e option to track changes
```
