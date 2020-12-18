import os.path

from bibtexparser.bibdatabase import BibDatabase

from .const import KEY_ID

def has_duplicates(bib_database):
    return len(bib_database.get_entry_dict()) != len(bib_database.get_entry_list())

# https://stackoverflow.com/a/9836685
def get_duplicates(bib_database):
    if isinstance(bib_database, BibDatabase):
        entries = bib_database.get_entry_list()
    else:
        entries = bib_database
    list_ids = [x[KEY_ID] for x in entries]
    return set([x for x in list_ids if list_ids.count(x) > 1])

def replace_duplicates(bib_database):
    if isinstance(bib_database, BibDatabase):
        entries = bib_database.get_entry_list()
    else:
        entries = bib_database
    duplicates = {k: 0 for k in get_duplicates(entries)}
    for entry in entries:
        _id = entry[KEY_ID]
        if _id in duplicates:
            duplicates[_id] += 1
            _id = "{}:{}".format(_id, chr(ord('`')+duplicates[_id]))
            entry[KEY_ID] = _id
    return entries
