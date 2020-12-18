import os.path

def has_duplicates(bib_database):
    return len(bib_database.get_entry_dict()) != len(bib_database.get_entry_list())
