import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser import bibdatabase
from bibtexparser.bibdatabase import BibDatabase

def load_abbr(abbr_file):
    with open(abbr_file, encoding="utf-8") as _abbr_file:
        parser = BibTexParser(homogenize_fields=True, common_strings=True)
        abbr_database = bibtexparser.load(_abbr_file, parser=parser)
    return abbr_database.strings

def load_bib_file(bib_file, abbr=None):
    if abbr is not None:
        bibdatabase.COMMON_STRINGS.update(abbr)
    with open(bib_file, encoding="utf-8") as _bib_file:
        parser = BibTexParser(homogenize_fields=True, common_strings=True)
        bib_database = bibtexparser.load(_bib_file, parser=parser)
    return bib_database
