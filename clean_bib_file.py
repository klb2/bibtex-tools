import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

KEY_MONTH = "month"

def substitute_month(month):
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
    return MONTH_DICTget(month_str, month_str)

def main(bib_file, remove_fields=None):
    if remove_fields is None:
        remove_fields = []
    with open(bib_file) as _bib_file:
        parser = BibTexParser(homogenize_fields=True)
        bib_database = bibtexparser.load(_bib_file, parser=parser)
    _clean_entries = []
    for entry in bib_database.get_entry_list():
        month = entry.get(KEY_MONTH)
        if month is not None:
            entry[KEY_MONTH] = substitute_month(month)
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
    args = vars(parser.parse_args())
    main(**args)
