import os.path
import logging
import re

import feedparser
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
KEY_EPRINT = "eprint"
KEY_ARCHIVE = "archiveprefix"
KEY_CATEGORY = "primaryclass"

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

def clean_eprint(eprint):
    return eprint.strip("arXiv:")

def clean_title(title):
    return re.sub(r'([A-Z]{1,}\b)|([a-zA-Z]+[A-Z]+[a-zA-Z\b]*)', r'{\g<0>}', title)

CLEAN_FUNC = {KEY_PAGES: clean_pages,
              KEY_MONTH: clean_month,
              KEY_EPRINT: clean_eprint,
              KEY_TITLE: clean_title}


def _remove_unwanted_characters(string):
    return re.sub(r'[{}]|(\\.)', '', string)

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
    last_name = _remove_unwanted_characters(last_name)
    last_name = last_name.replace(" ", "")
    #first_word = re.findall(r"[\w']+", title)[0]  # this gives "a" as first word
    first_word = re.findall(r"[\w']{3,}", title)[0]
    new_id = "{}{}{}".format(last_name, year, first_word.lower())
    return new_id

def get_arxiv_category(eprint):
    base_url = 'http://export.arxiv.org/api/query?'
    search_query = {'id_list': eprint,}
    query = "&".join(["{}={}".format(k, v) for k, v in search_query.items()])
    feed = feedparser.parse(base_url + query)
    entries = feed['entries']
    if len(entries) != 1:
        return None
    #a_id = entries[0]["id"].split('/abs/')[-1]
    try:
        primary_class = entries[0]['arxiv_primary_category']['term']
    except KeyError:
        return None
    if primary_class == "":
        return None
    else:
        return primary_class

def clean_bib_main(bib_file, remove_fields=None, replace_ids=False,
                   arxiv=False, verbose=logging.WARN, output=None):
    encoding = 'utf-8'
    logging.basicConfig(format="%(asctime)s - [%(levelname)8s]: %(message)s")
    logger = logging.getLogger('clean_bib_file')
    logger.setLevel(verbose)
    logger.info("Cleaning bib file: %s", bib_file)

    if remove_fields is None:
        remove_fields = []
    logger.info("Fields to remove: {}".format(remove_fields))

    with open(bib_file, encoding=encoding) as _bib_file:
        parser = BibTexParser(homogenize_fields=True, common_strings=True)
        bib_database = bibtexparser.load(_bib_file, parser=parser)
    logger.debug("Successfully loaded bib file")

    _clean_entries = []
    for entry in bib_database.get_entry_list():
        logger.info("Working on entry: %s", entry.get(KEY_ID))
        for _key, _clean_func in CLEAN_FUNC.items():
            _value = entry.get(_key)
            if _value is not None:
                logger.debug("Cleaning field: %s", _key)
                entry[_key] = _clean_func(_value)
        if arxiv:
            eprint = entry.get(KEY_EPRINT)
            primary_class = entry.get(KEY_CATEGORY)
            if (eprint is not None) and (primary_class is None):
                logging.debug("Retrieving arXiv primary category")
                _primary_class = get_arxiv_category(eprint)
                if _primary_class is not None:
                    entry[KEY_ARCHIVE] = "arXiv"
                    entry[KEY_CATEGORY] = _primary_class
                    logging.debug("Primary category successfully changed to: %s", _primary_class)
        for _field in remove_fields:
            logger.debug("Removing field: %s", _field)
            entry.pop(_field, None)
        if replace_ids:
            logger.debug("Replacing bib ID")
            entry[KEY_ID] = replace_bib_id(entry)
        _clean_entries.append(entry)
    clean_database = BibDatabase()
    clean_database.entries = _clean_entries
    if output is None:
        _out_dir, _out_base = os.path.split(bib_file)
        output = os.path.join(_out_dir, "clean-{}".format(_out_base))
    logger.info("Saving cleaned entries to: %s", output)
    with open(output, 'w', encoding=encoding) as out_file:
        writer = BibTexWriter()
        writer.add_trailing_comma = True
        writer.indent = "\t"  # "  "
        out_file.write(writer.write(clean_database))
    logger.info("Successfully saved new file.")
