import pytest

import bibtexparser
from bibtexparser.bparser import BibTexParser

from bibtextools.util import load_bib_file, load_abbr


ABBR = "abbr.bib"
DIRTY_BIB = "dirty.bib"

def test_replace_abbr_from_file():
    bib_data = load_bib_file(DIRTY_BIB, abbr=ABBR)
    entry = bib_data.get_entry_dict()["Cesar2013"]
    assert entry['journal'] == "Super Long Text"

def test_load_abbr_from_file():
    abbr = load_abbr(ABBR)
    assert abbr["my_abbr"] == "Super Long Text"
