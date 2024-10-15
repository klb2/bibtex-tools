import functools
import logging

from bibtexparser.bibdatabase import BibDatabase

from .clean_bib_file import replace_duplicate_ids, remove_duplicate_entries
from .modernize_bib_file import replace_bib_id
from .util import load_bib_file


def combine_bib_entries(bib_entries):
    bib_entries = [k.get_entry_list() if isinstance(k, BibDatabase) else k
                   for k in bib_entries]
    combined_entries = sum(bib_entries, [])
    return combined_entries



def combine_bib_files_main(bib_files, allow_duplicates=False, force=False,
                           replace_ids=False, verbose=logging.WARN, 
                           encoding='utf-8'):
    logging.basicConfig(format="%(asctime)s - [%(levelname)8s]: %(message)s")
    logger = logging.getLogger('combine_bib_files')
    logger.setLevel(verbose)
    logger.info("Combining bib files: %s", bib_files)
    #if abbr_file is not None:
    #    logger.info("Using the following abbreviation file: %s", abbr_file)
    bib_databases = [load_bib_file(_bib_file, abbr=None, encoding=encoding)
                     for _bib_file in bib_files]
    combined_entries = combine_bib_entries(bib_databases)
    combined_entries = remove_duplicate_entries(combined_entries, force=force, verbose=verbose)
    logger.debug("Successfully removed duplicates")
    #if replace_ids:
    #    combined_entries = #TODO: Adjust modernize function to support lists as input
    if not allow_duplicates:
        combined_entries = replace_duplicate_ids(combined_entries)
    return combined_entries
