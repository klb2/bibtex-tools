from bibtextools import clean_bib_file
from bibtextools.util import load_bib_file
from bibtextools.const import KEY_ID

DIRTY = "duplicates.bib"

def test_duplicate_check():
    bib_database = load_bib_file(DIRTY)
    assert clean_bib_file.has_duplicates(bib_database) == True

def test_get_duplicates_database():
    bib_database = load_bib_file(DIRTY)
    duplicates = clean_bib_file.get_duplicates(bib_database)
    assert duplicates == {"Author2020", "KEY"}

def test_get_duplicates_list():
    bib_database = load_bib_file(DIRTY)
    entries = bib_database.get_entry_list()
    duplicates = clean_bib_file.get_duplicates(entries)
    assert duplicates == {"Author2020", "KEY"}

def test_replace_duplicates():
    bib_database = load_bib_file(DIRTY)
    entries = bib_database.get_entry_list()
    clean_entries = clean_bib_file.replace_duplicates(entries)
    clean_ids = set([x[KEY_ID] for x in clean_entries])
    assert clean_ids == {"Author2020:a","Author2020:b","Author2020:c",
                         "KEY:a","KEY:b", "RemoveFields"}

def test_replace_duplicates_return():
    bib_database = load_bib_file(DIRTY)
    entries = bib_database.get_entry_list()
    clean_entries, duplicates = clean_bib_file.replace_duplicates(entries, return_dupl=True)
    assert duplicates == {"Author2020": 3, "KEY": 2}

def test_remove_fields():
    bib_database = load_bib_file(DIRTY)
    entries = bib_database.get_entry_list()
    clean_entries = clean_bib_file.remove_fields_from_entries(entries, ['abstract', 'annote'])
    _old_entry = [k for k in entries if k['ID'] == "RemoveFields"][0]
    _clean_entry = [k for k in clean_entries if k['ID'] == "RemoveFields"][0]
    assert (("abstract" in _old_entry) and ("annote" in _old_entry) and
           ("abstract" not in _clean_entry) and ("annote" not in _clean_entry))
