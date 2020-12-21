import logging
import copy
import functools

from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.customization import string_to_latex

from .const import KEY_ID
from .util import load_bib_file, write_bib_database

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
def get_duplicates(entries):
    list_ids = [x[KEY_ID] for x in entries]
    return set([x for x in list_ids if list_ids.count(x) > 1])

@cleaning_function(on_all_entries=True)
def replace_duplicates(entries, return_dupl=False):
    duplicates = {k: 0 for k in get_duplicates(entries)}
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

def remove_fields_from_entry(entry, remove_fields=None):
    if remove_fields is None:
        return entry
    for _field in remove_fields:
        entry.pop(_field, None)
    return entry

remove_fields_from_database = cleaning_function()(remove_fields_from_entry)

def replace_unicode_in_entry(entry):
    for _field in entry:
        if _field not in ("ID",):
            entry[_field] = string_to_latex(entry[_field])
    return entry

replace_unicode_in_database = cleaning_function()(replace_unicode_in_entry)

def clean_bib_file_main(bib_file, abbr_file=None, remove_fields=None,
                        encoding="utf-8", verbose=logging.WARN, 
                        replace_unicode=False):
    logging.basicConfig(format="%(asctime)s - [%(levelname)8s]: %(message)s")
    logger = logging.getLogger('clean_bib_file')
    logger.setLevel(verbose)
    logger.info("Cleaning bib file: %s", bib_file)
    if abbr_file is not None:
        logger.info("Using the following abbreviation file: %s", abbr_file)
    bib_database = load_bib_file(bib_file, abbr=abbr_file, encoding=encoding)
    logger.debug("Loaded file and replaced abbreviation strings")
    clean_entries, duplicates = replace_duplicates(bib_database,
                                                   return_dupl=True)
    logger.info("Replaced %d duplicates", len(duplicates))
    logger.debug("The following duplicates were found: %s", duplicates)
    if remove_fields is not None:
        logger.info("Removing fields: %s", remove_fields)
        clean_entries = remove_fields_from_database(clean_entries, remove_fields)
    if replace_unicode:
        logger.info("Converting unicode characters")
        clean_entries = replace_unicode_in_database(clean_entries)
    return clean_entries
