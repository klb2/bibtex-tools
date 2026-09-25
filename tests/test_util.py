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

COMMENTS_BIB = "comments.bib"

def test_load_entries_with_comments():
    entries = load_bib_file(COMMENTS_BIB).get_entry_dict()
    assert set(entries) == {"FullLineComment", "TrailingComment",
                            "PercentInValues", "ParenEntry"}
    assert "note" not in entries["FullLineComment"]
    assert entries["FullLineComment"]["journal"] == "Journal Name"
    assert entries["TrailingComment"]["journal"] == "Journal Name"

def test_load_keeps_percent_in_values():
    entry = load_bib_file(COMMENTS_BIB).get_entry_dict()["PercentInValues"]
    assert entry["title"] == r'50\% of "Everything"'
    assert entry["note"] == "Improves by 20% on average"
    assert entry["url"] == "https://example.com/some%20file.pdf"

def test_load_warns_about_unreadable_entries(caplog):
    load_bib_file(COMMENTS_BIB)
    warnings = [r.getMessage() for r in caplog.records if r.levelname == "WARNING"]
    assert len(warnings) == 1
    assert ("MissingComma" in warnings[0] and "InComment" not in warnings[0]
            and "CommentedOut" not in warnings[0])

def test_load_no_warning_for_valid_file(caplog):
    load_bib_file("duplicates.bib")
    assert not [r for r in caplog.records if r.levelname == "WARNING"]
