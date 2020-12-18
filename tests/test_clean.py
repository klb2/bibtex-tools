from bibtextools import clean_bib_file
from bibtextools.util import load_bib_file

DIRTY = "duplicates.bib"

def test_duplicate_check():
    bib_database = load_bib_file(DIRTY)
    assert clean_bib_file.has_duplicates(bib_database) == True
