import re
import os.path

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser import bibdatabase
from bibtexparser.bibdatabase import BibDatabase

from .const import KEY_ID

def load_abbr(abbr_file, encoding="utf-8"):
    with open(abbr_file, encoding=encoding) as _abbr_file:
        parser = BibTexParser(homogenize_fields=True, common_strings=True)
        abbr_database = bibtexparser.load(_abbr_file, parser=parser)
    return abbr_database.strings

def load_bib_file(bib_file, abbr=None, encoding="utf-8"):
    if abbr is not None:
        if os.path.isfile(abbr):
            abbr = load_abbr(abbr, encoding=encoding)
        bibdatabase.COMMON_STRINGS.update(abbr)
    with open(bib_file, encoding=encoding) as _bib_file:
        parser = BibTexParser(homogenize_fields=True, common_strings=True,
                              ignore_nonstandard_types=False)
        parser.alt_dict.pop("keywords")
        bib_database = bibtexparser.load(_bib_file, parser=parser)
    return bib_database


def write_bib_database(entries, out_file, encoding="utf-8",
                       order_entries_by=(KEY_ID,)):
    clean_database = BibDatabase()
    clean_database.entries = entries
    with open(out_file, 'w', encoding=encoding) as _out_file:
        writer = BibTexWriter()
        writer.order_entries_by = order_entries_by
        writer.add_trailing_comma = True
        writer.indent = "\t"  # "  "
        _out_file.write(writer.write(clean_database))

def getnames(names):
    """This function is a slight modification of the function from bibtexparser
    `bibtexparser.customization.getnames`.
    """
    tidynames = []
    for namestring in names:
        namestring = namestring.strip()
        if len(namestring) < 1:
            continue
        if ',' in namestring:
            namesplit = namestring.split(',', 1)
            last = namesplit[0].strip()
            firsts = [i.strip() for i in namesplit[1].split()]
        elif namestring[0] == "{" and namestring[-1] == "}":
            tidynames.append(namestring)
            continue
        else:
            #shielded_names = re.findall(r'[{].*?[}]', namestring)
            shielded_names = re.findall(r'(\s|^)([{].*?[}])', namestring)
            if shielded_names:
                last = shielded_names.pop()
                last = last[1]
                if namestring.endswith(last):
                    firsts = namestring[:-len(last)].split()
                else:
                    firsts = [last]
                    last = namestring[len(last):] #removeprefix in Python 3.9+
            else:
                namesplit = namestring.split()
                last = namesplit.pop()
                firsts = [i.replace('.', '. ').strip() for i in namesplit]
        if last in ['jnr', 'jr', 'junior']:
            last = firsts.pop()
        for item in firsts:
            if item in ['ben', 'van', 'der', 'de', 'la', 'le']:
                last = firsts.pop() + ' ' + last
        if not firsts:
            tidynames.append(last)
        else:
            tidynames.append(last + ", " + ' '.join(firsts))
    return tidynames
