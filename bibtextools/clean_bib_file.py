import os.path
import logging
import copy

from bibtexparser.bibdatabase import BibDatabase

from .const import KEY_ID
from .util import load_bib_file, write_bib_database

def cleaning_function(func):
    def wrapper_clean_func(bib_database, *args, **kwargs):
        if isinstance(bib_database, BibDatabase):
            entries = bib_database.get_entry_list()
        else:
            entries = bib_database
        entries = copy.deepcopy(entries)
        return func(entries, *args, **kwargs)
    return wrapper_clean_func


def has_duplicates(bib_database):
    return len(bib_database.get_entry_dict()) != len(bib_database.get_entry_list())

# https://stackoverflow.com/a/9836685
@cleaning_function
def get_duplicates(entries):
    list_ids = [x[KEY_ID] for x in entries]
    return set([x for x in list_ids if list_ids.count(x) > 1])

@cleaning_function
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

@cleaning_function
def remove_fields(entries, fields_to_remove=None):
    if fields_to_remove is None:
        return entries
    for entry in entries:
        for _field in fields_to_remove:
            entry.pop(_field, None)
    return entries

def clean_bib_file_main(bib_file, abbr_file=None, encoding="utf-8",
                        verbose=logging.WARN, output=None):
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
