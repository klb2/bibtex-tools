import pytest

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

def test_author_getnames():
    old_names = ["Last, First", "{van Name}, First", "{One Single Name}",
                 "First {di Last Name}", "von Name, First", "CompanyName"]
    expected = ["Last, First", "{van Name}, First", "{One Single Name}",
                "{di Last Name}, First", "von Name, First", "CompanyName"]
    new_names = modernize_bib_file.getnames(old_names)
    print(old_names)
    print(new_names)
    assert new_names == expected

@pytest.mark.parametrize("title,expected",
                         [("MIMO", r"{MIMO}"), ("M2M", r"{M2M}"),
                          (r"Acro IN mmWave Title", r"Acro {IN} {mmWave} Title"),
                          (r"Math $\mu=\alpha$", r"Math {$\mu=\alpha$}"),
                          (r"Already {ACRO} in", r"Already {ACRO} in"),
                          (r"{Surrounding {ACRO}}", r"Surrounding {ACRO}"),
                          (r"5G should be SHIELded", r"{5G} should be {SHIELded}"),
                          (r"Regular title with Names", r'Regular title with Names'),
                         ])
def test_title_shielding_acronyms(title, expected):
    cleaned = modernize_bib_file.clean_title(title)
    assert cleaned == expected

@pytest.mark.parametrize("title,expected",
                         [("MIMO", r"{{MIMO}}"), ("M2M", r"{{M2M}}"),
                          (r"{MIMO}", r"{MIMO}"), (r"{M2M}", r"{M2M}"),
                          (r"Acro IN mmWave Title", r"{Acro {IN} {mmWave} Title}"),
                          (r"Math $\mu=\alpha$", r"{Math {$\mu=\alpha$}}"),
                          (r"Already {ACRO} in", r"{Already {ACRO} in}"),
                          (r"{Surrounding {ACRO}}", r"{Surrounding {ACRO}}"),
                          (r"{All in curly}", r"{All in curly}"),
                          (r"Regular title with Names", r'{Regular title with Names}'),
                         ])
def test_title_shielding(title, expected):
    cleaned = modernize_bib_file.clean_title(title, shield_title=True)
    assert cleaned == expected
