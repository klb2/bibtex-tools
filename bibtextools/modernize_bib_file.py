import logging
import re

import feedparser
from bibtexparser.customization import string_to_latex#, getnames
from pyiso4.ltwa import Abbreviate

from .util import load_bib_file, write_bib_database, getnames
from .const import (KEY_ARCHIVE, KEY_AUTHOR, KEY_CATEGORY, KEY_EPRINT, KEY_ID,
                    KEY_MONTH, KEY_PAGES, KEY_TITLE, KEY_YEAR, KEYS_JOURNAL,
                    KEY_ENTRYTYPE, KEY_BOOKTITLE)
from .clean_bib_file import has_duplicates, replace_duplicate_ids, remove_duplicate_entries


def clean_month(month, **kwargs):
    _month_str = str(month).lower()
    _month_str = _month_str.strip(".")
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
    return MONTH_DICT.get(_month_str, month)

def clean_pages(pages, **kwargs):
    _split = pages.split("-")
    if "" in _split:
        _split.remove("") # remove empty entries in case '--' was already used
    return "--".join(_split)

def clean_eprint(eprint, **kwargs):
    return eprint.strip("arXiv:")


def __surrounded_by_curly(title):
    return title.startswith(r"{") and title.endswith(r"}")

def clean_title(title, shield_title=False, **kwargs):
    _shielded = re.sub(r'([0-9A-Z]+\b)|([a-zA-Z]+[A-Z0-9]+[a-zA-Z\b]*)|(\$[\w\\+-=]*\$)', r'{\g<0>}', title)
    _shielded = re.sub(r'\{{2}((?:\{??[^\{]*?))\}{2}', r'{\g<1>}', _shielded)
    _re_inner_acro = r'\{((?:\{??[^\{]*?))\}'
    __without_inner = re.sub(_re_inner_acro, r"\g<1>", _shielded)
    __remove_curly_w_acros = __surrounded_by_curly(__without_inner)
    __remove_curly_wo_acros = (len(re.findall(_re_inner_acro, _shielded)) == 1) and __surrounded_by_curly(title)
    if __remove_curly_w_acros or __remove_curly_wo_acros:
        _shielded = _shielded[1:-1]
    if shield_title:
        _shielded = r'{' + _shielded + r'}'
    return _shielded

def clean_author(author, **kwargs):
    _names = getnames([i.strip() for i in author.replace('\n', ' ').split(" and ")])
    return " and ".join(_names)

CLEAN_FUNC = {KEY_PAGES: clean_pages,
              KEY_MONTH: clean_month,
              KEY_EPRINT: clean_eprint,
              KEY_TITLE: clean_title,
              KEY_AUTHOR: clean_author}


def _remove_unwanted_characters(string):
    return re.sub(r'[{}]|(\\.)', '', string)

def replace_bib_id(entry):
    author = entry.get(KEY_AUTHOR)
    year = entry.get(KEY_YEAR)
    title = entry.get(KEY_TITLE)
    if (author is None) or (year is None) or (title is None):
        return entry.get(KEY_ID)
    first_author = author.split(" and ")[0]
    last_name = first_author.split(",")[0]
    #last_name = last_name.replace(" ", "")
    #first_word = re.findall(r"[\w']+", title)[0]  # this gives "a" as first word
    first_word = re.findall(r"[\w]{3,}", title)
    first_word = next((k.lower() for k in first_word if (k.lower() not in ["the"])), "")
    new_id = "{}{}{}".format(last_name, year, first_word)
    new_id = string_to_latex(new_id)
    new_id = _remove_unwanted_characters(new_id)
    new_id = new_id.replace(" ", "")
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

def abbreviate_journalname(entry):
    entry = entry.copy()
    abbreviator = Abbreviate.create()
    if entry[KEY_ENTRYTYPE] == "inproceedings":
        conf = entry.get(KEY_BOOKTITLE, False)
        if conf:
            conf_abbr = abbreviator(conf)
            entry[KEY_BOOKTITLE] = conf_abbr
    for _key in KEYS_JOURNAL:
        journal = entry.get(_key, False)
        if not journal:
            continue
        journal_abbr = abbreviator(journal)
        entry[_key] = journal_abbr
    return entry

def modernize_bib_main(bib_file, remove_fields=None, replace_ids=False,
                       force=False, arxiv=False, iso4=False,
                       verbose=logging.WARN, encoding='utf-8', **kwargs):
    logging.basicConfig(format="%(asctime)s - [%(levelname)8s]: %(message)s")
    logger = logging.getLogger('modernize_bib_file')
    logger.setLevel(verbose)
    logger.info("Modernizing bib file: %s", bib_file)

    if remove_fields is None:
        remove_fields = []
    logger.info("Fields to remove: {}".format(remove_fields))

    bib_database = load_bib_file(bib_file, encoding=encoding)
    logger.debug("Successfully loaded bib file")
    bib_database = remove_duplicate_entries(bib_database, force=force, verbose=verbose)
    logger.debug("Successfully removed duplicates")
    #if has_duplicates(bib_database):
    #    logger.warning("The loaded bib-file has duplicates (same ID for multiple entries). Consider running this script with the --replace_ids option to get automatically rename them.")

    _clean_entries = []
    for entry in bib_database:
        logger.info("Working on entry: %s", entry.get(KEY_ID))
        for _key, _clean_func in CLEAN_FUNC.items():
            _value = entry.get(_key)
            if _value is not None:
                logger.debug("Cleaning field: %s", _key)
                entry[_key] = _clean_func(_value, **kwargs)
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
        if iso4:
            entry = abbreviate_journalname(entry)
        _clean_entries.append(entry)
    if replace_ids:
        _clean_entries = replace_duplicate_ids(_clean_entries)
    return _clean_entries
