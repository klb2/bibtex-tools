from bibtextools import clean_bib_file
from bibtextools.util import load_bib_file
from bibtextools.const import KEY_ID

DIRTY = "duplicates.bib"
UNICODE = "unicode.bib"
DUPLICATE_CONTENT = "duplicate_content.bib"

def test_duplicate_check():
    bib_database = load_bib_file(DIRTY)
    assert clean_bib_file.has_duplicates(bib_database) == True

def test_get_duplicate_ids_database():
    bib_database = load_bib_file(DIRTY)
    duplicates = clean_bib_file.get_duplicate_ids(bib_database)
    assert duplicates == {"Author2020", "KEY"}

def test_get_duplicate_ids_list():
    bib_database = load_bib_file(DIRTY)
    entries = bib_database.get_entry_list()
    duplicates = clean_bib_file.get_duplicate_ids(entries)
    assert duplicates == {"Author2020", "KEY"}

def test_replace_duplicate_ids():
    bib_database = load_bib_file(DIRTY)
    entries = bib_database.get_entry_list()
    clean_entries = clean_bib_file.replace_duplicate_ids(entries)
    clean_ids = set([x[KEY_ID] for x in clean_entries])
    assert clean_ids == {"Author2020","Author2020:b","Author2020:c",
                         "Author2020duplicate", "KEY","KEY:b", "RemoveFields"}

def test_replace_duplicate_ids_keeps_first():
    bib_database = load_bib_file(DIRTY)
    entries = bib_database.get_entry_list()
    clean_entries = clean_bib_file.replace_duplicate_ids(entries)
    assert ([x[KEY_ID] for x in clean_entries if x[KEY_ID].startswith("KEY")]
            == ["KEY", "KEY:b"])
    assert clean_entries[0] == entries[0]

def test_replace_duplicate_ids_avoids_existing_ids():
    entries = [{KEY_ID: "A"}, {KEY_ID: "A"}, {KEY_ID: "A:b"}, {KEY_ID: "A"}]
    clean_entries = clean_bib_file.replace_duplicate_ids(entries)
    assert [x[KEY_ID] for x in clean_entries] == ["A", "A:c", "A:b", "A:d"]

def test_replace_duplicate_ids_return():
    bib_database = load_bib_file(DIRTY)
    entries = bib_database.get_entry_list()
    clean_entries, duplicates = clean_bib_file.replace_duplicate_ids(entries, return_dupl=True)
    assert duplicates == {"Author2020": 3, "KEY": 2}

def test_remove_fields():
    bib_database = load_bib_file(DIRTY)
    entries = bib_database.get_entry_list()
    clean_entries = clean_bib_file.remove_fields_from_database(entries, ['abstract', 'annote'])
    _old_entry = [k for k in entries if k['ID'] == "RemoveFields"][0]
    _clean_entry = [k for k in clean_entries if k['ID'] == "RemoveFields"][0]
    assert (("abstract" in _old_entry) and ("annote" in _old_entry) and
           ("abstract" not in _clean_entry) and ("annote" not in _clean_entry))

def test_replace_unicode():
    bib_database = load_bib_file(UNICODE)
    entries = bib_database.get_entry_dict()
    key = "Cesar2013"
    clean_entry = clean_bib_file.replace_unicode_in_entry(entries[key].copy())
    assert ((entries[key]['author'] == "Jean César") and
            (clean_entry['author'] == r'Jean C{\'e}sar'))

def test_not_replace_converted_unicode():
    bib_database = load_bib_file(UNICODE)
    entries = bib_database.get_entry_dict()
    key = "Author1970"
    clean_entry = clean_bib_file.replace_unicode_in_entry(entries[key].copy())
    assert ((clean_entry['author'] == r"Bj{\"o}rn Author") and
            (clean_entry["journal"] == r'With 6$\times$6 math expressions') and
            (clean_entry['pages'] == r'12 \& 13'))

def test_get_duplicate_entries_number():
    bib_database = clean_bib_file.load_bib_file(DUPLICATE_CONTENT)
    results = clean_bib_file.get_duplicate_entries(bib_database)
    assert len(results) == 2

def test_remove_duplicate_entries_number_forced():
    bib_database = clean_bib_file.load_bib_file(DUPLICATE_CONTENT)
    results = clean_bib_file.remove_duplicate_entries(bib_database, force=True)
    _entry = next(x for x in results if x[KEY_ID] == "Part2")
    assert ((len(bib_database.get_entry_list()) == 9) and
            (len(results) == 7) and len(_entry) == 11)

def test_remove_duplicate_entries_interactive_empty_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt="": "")
    bib_database = clean_bib_file.load_bib_file(DUPLICATE_CONTENT)
    results = clean_bib_file.remove_duplicate_entries(bib_database)
    _entry = next(x for x in results if x[KEY_ID] == "Part2")
    assert len(results) == 7 and len(_entry) == 11

def test_remove_duplicate_entries_interactive_skip(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt="": "0")
    bib_database = clean_bib_file.load_bib_file(DUPLICATE_CONTENT)
    results = clean_bib_file.remove_duplicate_entries(bib_database)
    assert len(results) == len(bib_database.get_entry_list()) == 9

def test_remove_duplicate_entries_interactive_invalid_input(monkeypatch):
    answers = ["3", "-1", "abc", "", ""]
    monkeypatch.setattr("builtins.input", lambda _prompt="": answers.pop(0))
    bib_database = clean_bib_file.load_bib_file(DUPLICATE_CONTENT)
    results = clean_bib_file.remove_duplicate_entries(bib_database)
    _entry = next(x for x in results if x[KEY_ID] == "Part2")
    assert len(results) == 7 and len(_entry) == 11 and not answers

def test_remove_duplicate_entries_interactive_skip_not_asked_again(monkeypatch):
    answers = ["0", "2"]
    monkeypatch.setattr("builtins.input", lambda _prompt="": answers.pop(0))
    bib_database = clean_bib_file.load_bib_file(DUPLICATE_CONTENT)
    results = clean_bib_file.remove_duplicate_entries(bib_database)
    _ids = set([x[KEY_ID] for x in bib_database.get_entry_list()])
    assert set([x[KEY_ID] for x in results]) == _ids - {"Part2dupl"} and not answers
