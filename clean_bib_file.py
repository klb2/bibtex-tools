import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

KEY_MONTH = "month"
KEY_PAGES = "pages"

def clean_month(month):
    month_str = str(month).lower()
    MONTH_DICT = {"jan": "1",
                  "january": "1",
                  "1": "1",
                  "feb": "2",
                  "february": "2",
                  "2": "2",
                  "mar": "3",
                  "march": "3",
                  "3": "3",
                  "apr": "4",
                  "april": "4",
                  "4": "4",
                  "may": "5",
                  "5": "5",
                  "jun": "6",
                  "june": "6",
                  "6": "6",
                  "jul": "7",
                  "july": "7",
                  "7": "7",
                  "aug": "8",
                  "august": "8",
                  "8": "8",
                  "sep": "9",
                  "september": "9",
                  "9": "9",
                  "oct": "10",
                  "october": "10",
                  "10": "10",
                  "nov": "11",
                  "november": "11",
                  "11": "11",
                  "dec": "12",
                  "december": "12",
                  "12": "12",
                 }
    return MONTH_DICT.get(month_str, month_str)

def clean_pages(pages):
    _split = pages.split("-")
    if "" in _split:
        _split.remove("") # remove empty entries in case '--' was already used
    return "--".join(_split)

CLEAN_FUNC = {KEY_PAGES: clean_pages,
              KEY_MONTH: clean_month}

def main(bib_file, remove_fields=None, replace_keys=False):
    if remove_fields is None:
        remove_fields = []
    with open(bib_file) as _bib_file:
        parser = BibTexParser(homogenize_fields=True)
        bib_database = bibtexparser.load(_bib_file, parser=parser)
    _clean_entries = []
    for entry in bib_database.get_entry_list():
        for _key, _clean_func in CLEAN_FUNC.items():
            _value = entry.get(_key)
            if _value is not None:
                entry[_key] = _clean_func(_value)
        for _field in remove_fields:
            entry.pop(_field, None)
        _clean_entries.append(entry)
    clean_database = BibDatabase()
    clean_database.entries = _clean_entries
    outfile = "clean-{}".format(bib_file)
    with open(outfile, 'w') as out_file:
        writer = BibTexWriter()
        writer.add_trailing_comma = True
        writer.indent = "\t"  # "  "
        out_file.write(writer.write(clean_database))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("bib_file")
    parser.add_argument("-r", "--remove_fields", nargs="*", default=["abstract", "annote", "file", "keyword"])
    parser.add_argument("--replace_keys", action="store_true")
    args = vars(parser.parse_args())
    main(**args)
