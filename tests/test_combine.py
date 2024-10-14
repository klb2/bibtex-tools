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
    assert len(combined_entries) == 9

def test_combine_main_len():
    combined_entries = combine_bib_files.combine_bib_files_main(BIB_FILES,
                                                                force=True)
    assert len(combined_entries) == 8

def test_combine_main_allow_duplicates():
    combined_entries = combine_bib_files.combine_bib_files_main(BIB_FILES,
                                                                allow_duplicates=True,
                                                                force=True)
    combined_ids = set([x[KEY_ID] for x in combined_entries])
    print(combined_ids)
    assert (len(combined_entries) == 8 and
            combined_ids == {"Author2020", "KEY", "RemoveFields", "Cesar2013",
                             "Author1970", "Author2020duplicate"})

def test_combine_main_replace_duplicates():
    combined_entries = combine_bib_files.combine_bib_files_main(BIB_FILES,
                                                                allow_duplicates=False,
                                                                force=True)
    combined_ids = set([x[KEY_ID] for x in combined_entries])
    assert combined_ids == {"Author2020:a", "Author2020:b",
                            "KEY:a", "KEY:b", "RemoveFields", "Cesar2013",
                            "Author1970", "Author2020duplicate"}
