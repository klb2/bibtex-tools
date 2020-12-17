import os.path

import numpy as np
import pytest

import bibtexparser
from bibtexparser.bparser import BibTexParser

from bibtextools import clean_bib_file


BIB_MAIN = "old.bib"
CLEAN_BIB_MAIN = "clean-old.bib"

def test_main(tmpdir, bib_file=BIB_MAIN):
    out_file = os.path.join(tmpdir, CLEAN_BIB_MAIN)
    clean_bib_file.clean_bib_main(bib_file, output=out_file)
    with open(out_file, encoding="utf-8") as _bib_file:
        parser = BibTexParser(homogenize_fields=True, common_strings=True)
        bib_database = bibtexparser.load(_bib_file, parser=parser)
    assert len(bib_database.get_entry_list()) == 5

def test_replace_id(tmpdir, bib_file=BIB_MAIN):
    out_file = os.path.join(tmpdir, CLEAN_BIB_MAIN)
    clean_bib_file.clean_bib_main(bib_file, output=out_file, replace_ids=True)
    with open(out_file, encoding="utf-8") as _bib_file:
        parser = BibTexParser(homogenize_fields=True, common_strings=True)
        clean_bib_database = bibtexparser.load(_bib_file, parser=parser)
    expected_keys = set(["Name2010title", "MultipleWordName2010title",
                         "Jorswieck2020copula", "Duck2018ecg",
                         "AuthorwithLastNames2015title"])
    cleaned_keys = set([k[clean_bib_file.KEY_ID]
                        for k in clean_bib_database.get_entry_list()])
    assert cleaned_keys == expected_keys
