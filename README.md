# BibTeX Tools

This repository contains a collection of functions that might be helpful when
working with BibTeX files (`*.bib`).

Right now, the following functions are available

* Cleaning bib files: The script `clean_bib_file.py` allows to clean bib-files
  and replaces deprecated commands with new ones, e.g., the old month entries
  are replaced by the number of the months.
  There also is an option to download information from arXiv.
  It is invoked by `bibtex-tools myfile.bib`.

Use `bibtex-tools --help` to list possible command options.
