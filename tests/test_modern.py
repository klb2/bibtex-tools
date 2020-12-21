import bibtexparser
from bibtexparser.bparser import BibTexParser

from bibtextools import modernize_bib_file


BIB_MAIN = "old.bib"

def test_main_modern(bib_file=BIB_MAIN):
    clean_entries = modernize_bib_file.modernize_bib_main(bib_file)
    assert len(clean_entries) == 6

def test_replace_id(bib_file=BIB_MAIN):
    clean_entries = modernize_bib_file.modernize_bib_main(bib_file, replace_ids=True)
    expected_keys = set(["Name2010title", "MultipleWordName2010title",
                         "Jorswieck2020copula", "Duck2018ecg",
                         "AuthorwithLastNames2015title", "Report2005"])
    cleaned_keys = set([k[modernize_bib_file.KEY_ID]
                        for k in clean_entries])
    assert cleaned_keys == expected_keys

def test_arxiv_primaryclass(bib_file=BIB_MAIN):
    clean_entries = modernize_bib_file.modernize_bib_main(bib_file, arxiv=True)
    _entry = [k for k in clean_entries
              if k[modernize_bib_file.KEY_ID] == "Besser2020CLpart1"][0]
    assert _entry[modernize_bib_file.KEY_CATEGORY] == "cs.IT"
