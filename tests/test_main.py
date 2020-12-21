import os.path
import sys

import pytest

import bibtexparser
from bibtexparser.bparser import BibTexParser

from bibtextools.__main__ import main


BIB_MAIN = "old.bib"
CLEAN_BIB_MAIN = "clean-old.bib"

def test_main(tmpdir, bib_file=BIB_MAIN):
    out_file = os.path.join(tmpdir, CLEAN_BIB_MAIN)
    sys.argv = [sys.argv[0], '-o', '{}'.format(out_file), 'modernize', bib_file]
    main()
    with open(out_file, encoding="utf-8") as _bib_file:
        parser = BibTexParser(homogenize_fields=True, common_strings=True)
        bib_database = bibtexparser.load(_bib_file, parser=parser)
    assert len(bib_database.get_entry_list()) == 6