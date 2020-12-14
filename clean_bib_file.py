import re

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

KEY_ID = "ID"
KEY_AUTHOR = "author"
KEY_MONTH = "month"
KEY_TITLE = "title"
KEY_PAGES = "pages"
KEY_YEAR = "year"

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

def _strip_curly_brackets(string):
    string = string.strip("{")
    string = string.strip("}")
    return string

def replace_bib_id(entry):
    author = entry.get(KEY_AUTHOR)
    year = entry.get(KEY_YEAR)
    title = entry.get(KEY_TITLE)
    if (author is None) or (year is None) or (title is None):
        return entry.get(KEY_ID)
    first_author = author.split(" and ")[0]
    if "," in first_author:
        last_name = first_author.split(",")[0]
    else:
        last_name = first_author.split(" ")[-1]
    last_name = _strip_curly_brackets(last_name)
    last_name = last_name.replace(" ", "")
    first_word = re.findall(r"[\w']+", title)[0]
    new_id = "{}{}{}".format(last_name, year, first_word.lower())
    return new_id

def main(bib_file, remove_fields=None, replace_ids=False):
    if remove_fields is None:
        remove_fields = []
    with open(bib_file) as _bib_file:
        parser = BibTexParser(homogenize_fields=True, common_strings=True)
        bib_database = bibtexparser.load(_bib_file, parser=parser)
    _clean_entries = []
    for entry in bib_database.get_entry_list():
        for _key, _clean_func in CLEAN_FUNC.items():
            _value = entry.get(_key)
            if _value is not None:
                entry[_key] = _clean_func(_value)
        for _field in remove_fields:
            entry.pop(_field, None)
        if replace_ids:
            entry[KEY_ID] = replace_bib_id(entry)
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
    parser.add_argument("--replace_ids", action="store_true")
    args = vars(parser.parse_args())
    main(**args)
