import pytest

from bibtextools import combine_bib_files
from bibtextools.util import load_bib_file
from bibtextools.const import KEY_ID

BIB_FILES = ["duplicates.bib", "unicode.bib"]


@pytest.mark.parametrize("entry_list", (True, False))
def test_combine_databases(entry_list):
    if entry_list:
        bib_databases = [load_bib_file(b).get_entry_list() for b in BIB_FILES]
    else:
        bib_databases = [load_bib_file(b) for b in BIB_FILES]
    combined_entries = combine_bib_files.combine_bib_entries(bib_databases)
    assert len(combined_entries) == 7

def test_combine_main_len():
    combined_entries = combine_bib_files.combine_bib_files_main(BIB_FILES)
    assert len(combined_entries) == 7

def test_combine_main_replace_duplicates():
    combined_entries = combine_bib_files.combine_bib_files_main(BIB_FILES,
                                                                remove_duplicates=True)
    combined_ids = set([x[KEY_ID] for x in combined_entries])
    assert combined_ids == {"Author2020:a","Author2020:b","Author2020:c",
                            "KEY:a","KEY:b", "RemoveFields", "Cesar2013"}
