from bibtextools import filter_bib_file
from bibtextools.const import KEY_ID

CROSSREF_BIB = "crossref.bib"
CROSSREF_BBL = "crossref.bbl"
NATBIB_BBL = "natbib.bbl"
BIBLATEX_BBL = "cited.bbl"


def test_bbl_keys_biblatex():
    keys, backend = filter_bib_file.get_bbl_keys(BIBLATEX_BBL)
    assert keys == {"Key123", "Conference2015", "NotInBib"} and backend == "biblatex"

def test_bbl_keys_bibtex_wrapped_labels():
    keys, backend = filter_bib_file.get_bbl_keys(NATBIB_BBL)
    assert (keys == {"Name2010", "Jorswieck2020", "Duck2018", "Report2005"}
            and backend == "bibtex")

def test_bibitem_label_with_bracket():
    keys = filter_bib_file.get_bibitem_keys(r"\bibitem[{[Anon] (2020)}]{Anon2020}")
    assert keys == {"Anon2020"}

def test_filter_keeps_referenced_entries():
    kept = filter_bib_file.filter_cited_main(CROSSREF_BIB, CROSSREF_BBL)
    assert set([x[KEY_ID] for x in kept]) == {"Child2022", "Proc2022",
                                              "PublisherInfo", "Main2023",
                                              "Data2023"}

def test_filter_warns_about_missing_cited_keys(caplog):
    filter_bib_file.filter_cited_main("old.bib", BIBLATEX_BBL)
    warnings = [r.getMessage() for r in caplog.records if r.levelname == "WARNING"]
    assert len(warnings) == 1 and "NotInBib" in warnings[0]
