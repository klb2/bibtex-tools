import os.path
import sys

import pytest
from click.testing import CliRunner

import bibtexparser
from bibtexparser.bparser import BibTexParser

from bibtextools.cli import main


BIB_MAIN = "old.bib"
SECOND_BIB = "unicode.bib"
CLEAN_BIB_MAIN = "clean-old.bib"

def test_main_modern(tmpdir, bib_file=BIB_MAIN):
    out_file = os.path.join(tmpdir, CLEAN_BIB_MAIN)
    runner = CliRunner()
    result = runner.invoke(main, f'-o "{out_file}" modernize {bib_file}')
    with open(out_file, encoding="utf-8") as _bib_file:
        parser = BibTexParser(homogenize_fields=True, common_strings=True)
        bib_database = bibtexparser.load(_bib_file, parser=parser)
    assert (len(bib_database.get_entry_list()) == 6) and (result.exit_code == 0)

def test_main_combine(tmpdir, bib_file=[BIB_MAIN, SECOND_BIB]):
    out_file = os.path.join(tmpdir, CLEAN_BIB_MAIN)
    runner = CliRunner()
    result = runner.invoke(main, f'-o "{out_file}" combine {bib_file[0]} {bib_file[1]}')
    with open(out_file, encoding="utf-8") as _bib_file:
        parser = BibTexParser(homogenize_fields=True, common_strings=True)
        bib_database = bibtexparser.load(_bib_file, parser=parser)
    assert len(bib_database.get_entry_list()) == 8
