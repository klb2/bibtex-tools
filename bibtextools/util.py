import logging
import re
import os.path
from collections import Counter

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser import bibdatabase
from bibtexparser.bibdatabase import BibDatabase

from .const import KEY_ID

def load_abbr(abbr_file, encoding="utf-8"):
    with open(abbr_file, encoding=encoding) as _abbr_file:
        parser = BibTexParser(homogenize_fields=True, common_strings=True)
        abbr_database = bibtexparser.load(_abbr_file, parser=parser)
    return abbr_database.strings

def strip_comments(bib_str):
    """Remove `%` comments between the fields of an entry, e.g., a commented
    out field, which make bibtexparser silently skip the entry. Commented
    lines between entries are removed as well. Field values are not changed.
    """
    stripped = []
    depth = 0
    in_quotes = False
    idx = 0
    while idx < len(bib_str):
        char = bib_str[idx]
        if char == "%" and not in_quotes and bib_str[idx-1] != "\\":
            _line_start = bib_str.rfind("\n", 0, idx) + 1
            if depth == 1 or (depth == 0 and
                              not bib_str[_line_start:idx].strip()):
                idx = bib_str.find("\n", idx)
                if idx < 0:
                    break
                continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth = max(depth-1, 0)
            if depth == 0:
                in_quotes = False
        elif char == '"' and depth == 1:
            in_quotes = not in_quotes
        stripped.append(char)
        idx += 1
    return "".join(stripped)

_RE_ENTRY_HEAD = re.compile(r'^[ \t]*@[ \t]*(\w+)[ \t]*[{(]\s*([^\s,{}]+)\s*,',
                            re.MULTILINE)
_RE_COMMENT_HEAD = re.compile(r'^[ \t]*@[ \t]*comment[ \t]*\{',
                              re.MULTILINE | re.IGNORECASE)

def get_entry_ids(bib_str):
    """Return the IDs of all entries that start on a new line in a bib
    string. Unlike a full parser, this does not depend on the content of the
    entries being valid."""
    comment_spans = []
    for _match in _RE_COMMENT_HEAD.finditer(bib_str):
        depth = 1
        idx = _match.end()
        while depth > 0 and idx < len(bib_str):
            depth += {"{": 1, "}": -1}.get(bib_str[idx], 0)
            idx += 1
        comment_spans.append((_match.start(), idx))
    ids = []
    for _match in _RE_ENTRY_HEAD.finditer(bib_str):
        if _match.group(1).lower() in ("comment", "preamble", "string"):
            continue
        if any(_start < _match.start() < _end
               for _start, _end in comment_spans):
            continue
        ids.append(_match.group(2))
    return ids

def load_bib_file(bib_file, abbr=None, encoding="utf-8"):
    logger = logging.getLogger('load_bib_file')
    if abbr is not None:
        if os.path.isfile(abbr):
            abbr = load_abbr(abbr, encoding=encoding)
        bibdatabase.COMMON_STRINGS.update(abbr)
    with open(bib_file, encoding=encoding) as _bib_file:
        bib_str = strip_comments(_bib_file.read())
    parser = BibTexParser(homogenize_fields=True, common_strings=True,
                          ignore_nonstandard_types=False)
    parser.alt_dict.pop("keywords")
    bib_database = bibtexparser.loads(bib_str, parser=parser)
    skipped = (Counter(get_entry_ids(bib_str))
               - Counter([x[KEY_ID] for x in bib_database.entries]))
    if skipped:
        logger.warning("Could not read %d entries from %s. They are NOT "
                       "included in the result. Check them for syntax "
                       "errors, e.g., a missing comma between fields: %s",
                       sum(skipped.values()), bib_file,
                       ", ".join(skipped.elements()))
    return bib_database


def write_bib_database(entries, out_file, encoding="utf-8",
                       order_entries_by=(KEY_ID,)):
    clean_database = BibDatabase()
    clean_database.entries = entries
    with open(out_file, 'w', encoding=encoding) as _out_file:
        writer = BibTexWriter()
        writer.order_entries_by = order_entries_by
        writer.add_trailing_comma = True
        writer.indent = "\t"  # "  "
        _out_file.write(writer.write(clean_database))

def getnames(names):
    """This function is a slight modification of the function from bibtexparser
    `bibtexparser.customization.getnames`.
    """
    tidynames = []
    for namestring in names:
        namestring = namestring.strip()
        if len(namestring) < 1:
            continue
        if ',' in namestring:
            namesplit = namestring.split(',', 1)
            last = namesplit[0].strip()
            firsts = [i.strip() for i in namesplit[1].split()]
        elif namestring[0] == "{" and namestring[-1] == "}":
            tidynames.append(namestring)
            continue
        else:
            #shielded_names = re.findall(r'[{].*?[}]', namestring)
            shielded_names = re.findall(r'(\s|^)([{].*?[}])', namestring)
            if shielded_names:
                last = shielded_names.pop()
                last = last[1]
                if namestring.endswith(last):
                    firsts = namestring[:-len(last)].split()
                else:
                    firsts = [last]
                    last = namestring[len(last):] #removeprefix in Python 3.9+
            else:
                namesplit = namestring.split()
                last = namesplit.pop()
                firsts = [i.replace('.', '. ').strip() for i in namesplit]
        if last in ['jnr', 'jr', 'junior']:
            last = firsts.pop()
        for item in firsts:
            if item in ['ben', 'van', 'der', 'de', 'la', 'le']:
                last = firsts.pop() + ' ' + last
        if not firsts:
            tidynames.append(last)
        else:
            tidynames.append(last + ", " + ' '.join(firsts))
    return tidynames
