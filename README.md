# BibTeX Tools

This repository contains a collection of functions that might be helpful when
working with BibTeX files (`*.bib`).

Right now, the following functions are available

* Cleaning bib files: The script `clean_bib_file.py` allows to clean bib-files
  and replaces deprecated commands with new ones, e.g., the old month entries
  are replaced by the number of the months.
  There also is an option to download information from arXiv.


## TODOs
The following features are planned
* Automatically use curly brackets for acronyms (regular expressions, e.g.,
  `re.sub(r'[A-Z]{2,}', r'{\g<0>}', title)`)
* Deal with multiple URLs that are separated by space, e.g., when exporting
  from Mendeley
* Maybe there is an issue when both URL and DOI are provided. Maybe delete URL,
  if DOI is specified
* Test unicode support
* Check for duplicates, i.e., the same ID used multiple times. Maybe
  `bibtexparser` does this already?!
* Add setup and entry points for script and upload it to PyPI
