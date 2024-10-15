import logging
import copy
import functools
import re
import itertools
from difflib import SequenceMatcher
from pprint import pprint

from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.customization import string_to_latex, convert_to_unicode

from .const import KEY_ID, KEY_TITLE, KEY_AUTHOR, KEY_ENTRYTYPE, KEYS_JOURNAL, KEY_BOOKTITLE, KEY_YEAR, KEY_PAGES
from .util import load_bib_file, write_bib_database, getnames

def repeat(num_times):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(*args, **kwargs):
            for _ in range(num_times):
                value = func(*args, **kwargs)
            return value
        return wrapper_repeat
    return decorator_repeat


def cleaning_function(on_all_entries=False):
    def decorator_cleaning_function(func):
        @functools.wraps(func)
        def wrapper_clean_func(bib_database, *args, **kwargs):
            if isinstance(bib_database, BibDatabase):
                entries = bib_database.get_entry_list()
            else:
                entries = bib_database
            entries = copy.deepcopy(entries)
            if not on_all_entries:
                for entry in entries:
                    entry = func(entry, *args, **kwargs)
            else:
                entries = func(entries, *args, **kwargs)
            return entries
        return wrapper_clean_func
    return decorator_cleaning_function


def has_duplicates(bib_database):
    return len(bib_database.get_entry_dict()) != len(bib_database.get_entry_list())

# https://stackoverflow.com/a/9836685
@cleaning_function(on_all_entries=True)
def get_duplicate_ids(entries):
    list_ids = [x[KEY_ID] for x in entries]
    return set([x for x in list_ids if list_ids.count(x) > 1])

@cleaning_function(on_all_entries=True)
def replace_duplicate_ids(entries, return_dupl=False):
    duplicates = {k: 0 for k in get_duplicate_ids(entries)}
    for entry in entries:
        _id = entry[KEY_ID]
        if _id in duplicates:
            duplicates[_id] += 1
            _id = "{}:{}".format(_id, chr(ord('`')+duplicates[_id]))
            entry[KEY_ID] = _id
    if return_dupl:
        return entries, duplicates
    else:
        return entries

@cleaning_function(on_all_entries=True)
def get_duplicate_entries(entries):
    seq_matcher_title = SequenceMatcher()
    seq_matcher_authors = SequenceMatcher()
    duplicates = []
    for _entry1, _entry2 in itertools.combinations(entries, 2):
        if _entry1[KEY_ENTRYTYPE] != _entry2[KEY_ENTRYTYPE]:
            continue
        seq_matcher_title.set_seqs(_entry2[KEY_TITLE], _entry1[KEY_TITLE])
        _title_ratio = seq_matcher_title.ratio()
        if _title_ratio < .8:
            continue
        #print('---')
        #print(f"T1: {_entry1[KEY_TITLE]}\nT2: {_entry2[KEY_TITLE]}")
        #print(f"Ratio: {_title_ratio}")
        _authors1 = getnames([i.strip() for i in _entry1[KEY_AUTHOR].replace('\n', ' ').split(" and ")])
        _authors1 = " and ".join(_authors1)
        _authors2 = getnames([i.strip() for i in _entry2[KEY_AUTHOR].replace('\n', ' ').split(" and ")])
        _authors2 = " and ".join(_authors2)
        seq_matcher_authors.set_seqs(_authors2, _authors1)
        _author_ratio = seq_matcher_authors.ratio()
        if _author_ratio < .9:
            continue
        _same_misc = True
        if _entry1[KEY_ENTRYTYPE] == "inproceedings":
            _same_misc = _same_misc and (_entry1.get(KEY_YEAR, "") == _entry2.get(KEY_YEAR, ""))
            _same_misc = _same_misc and (SequenceMatcher(None, _entry1.get(KEY_BOOKTITLE, ""), _entry2.get(KEY_BOOKTITLE, "")).ratio() > .7)
        elif _entry1[KEY_ENTRYTYPE] == "article":
            for _key in KEYS_JOURNAL:
                _journal1 = _entry1.get(_key, "")
                if _journal1: break
            for _key in KEYS_JOURNAL:
                _journal2 = _entry2.get(_key, "")
                if _journal2: break
            _same_misc = SequenceMatcher(None, _journal1, _journal2).ratio() > .7
            if KEY_PAGES in _entry1 and KEY_PAGES in _entry2:
                _same_misc = _same_misc and (SequenceMatcher(None, _entry1[KEY_PAGES], _entry2[KEY_PAGES]).ratio() >= .75)
        if not _same_misc:
            continue
        duplicates.append((_entry1, _entry2))
    return duplicates

@cleaning_function(on_all_entries=True)
def remove_duplicate_entries(entries, force=False, verbose=logging.WARN):
    logger = logging.getLogger('remove_duplicate_entries')
    logger.setLevel(verbose)
    duplicates = get_duplicate_entries(entries)
    if duplicates:
        logger.warning("Found %d duplicate pairs", len(duplicates))
    else:
        logger.info("No duplicate citations found.")
    while duplicates:
        _pair = duplicates[0]
        _shorter_entry = sorted(_pair, key=len)[0]
        if force:
            logger.info("Due to --force argument, deleting the entry with less fields (without asking)...")
            entries.remove(_shorter_entry)
        else:
            logger.warning("Pair of duplicate entries:")
            logger.warning("Entry 1:")
            pprint(_pair[0])
            logger.warning("Entry 2:")
            pprint(_pair[1])
            _idx_entry_delete = input("Which entry do you want to REMOVE? Type 1 or 2 and hit enter. Simply hitting enter will remove the shorter entry.\n")
            try:
                _idx_entry_delete = int(_idx_entry_delete) - 1
                entries.remove(_pair[_idx_entry_delete])
            except ValueError:
                entries.remove(_shorter_entry)
        logger.info("Successfully removed duplicate entry.")
        duplicates = get_duplicate_entries(entries)
        logger.info("%d duplicate pairs remaining...", len(duplicates))
    return entries

def remove_fields_from_entry(entry, remove_fields=None):
    if remove_fields is None:
        return entry
    for _field in remove_fields:
        entry.pop(_field, None)
    return entry

remove_fields_from_database = cleaning_function()(remove_fields_from_entry)

def _replace_textbackslash(matchobj):
    return matchobj.group(0).replace(r'\textbackslash ', '\\')

def replace_unicode_in_entry(entry):
    entry = convert_to_unicode(entry)
    for _field in entry:
        if _field not in ("ID",):
            unicode_free = string_to_latex(entry[_field])
            math_dollar = re.sub(r'\\textdollar (.*?)( *)\\textdollar ', r'$\g<1>$', unicode_free)
            entry[_field] = re.sub(r'\$(.*)(\\textbackslash )(.*)\$', _replace_textbackslash, math_dollar)
    return entry

replace_unicode_in_database = cleaning_function()(replace_unicode_in_entry)

def clean_bib_file_main(bib_file, abbr_file=None, remove_fields=None,
                        encoding="utf-8", force=False, verbose=logging.WARN, 
                        replace_unicode=False):
    logging.basicConfig(format="%(asctime)s - [%(levelname)8s]: %(message)s")
    logger = logging.getLogger('clean_bib_file')
    logger.setLevel(verbose)
    logger.info("Cleaning bib file: %s", bib_file)
    if abbr_file is not None:
        logger.info("Using the following abbreviation file: %s", abbr_file)
    bib_database = load_bib_file(bib_file, abbr=abbr_file, encoding=encoding)
    logger.debug("Loaded file and replaced abbreviation strings")
    bib_database = remove_duplicate_entries(bib_database, force=force, verbose=verbose)
    logger.debug("Successfully removed duplicates")
    clean_entries, duplicates = replace_duplicate_ids(bib_database,
                                                      return_dupl=True)
    logger.info("Replaced %d duplicate ids", len(duplicates))
    logger.debug("The following duplicates were found: %s", duplicates)
    if remove_fields is not None:
        logger.info("Removing fields: %s", remove_fields)
        clean_entries = remove_fields_from_database(clean_entries, remove_fields)
    if replace_unicode:
        logger.info("Converting unicode characters")
        clean_entries = replace_unicode_in_database(clean_entries)
    return clean_entries
