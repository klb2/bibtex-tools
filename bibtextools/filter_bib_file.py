import logging
import re

from .const import KEY_ID, KEYS_REFERENCE
from .util import load_bib_file


_RE_BIBITEM = re.compile(r"\\bibitem(?![a-zA-Z])\s*")
_RE_BIBITEM_KEY = re.compile(r"\s*\{([^}]+)\}")

def get_bibitem_keys(content):
    """Return the keys of all `\\bibitem[label]{key}` in a BibTeX .bbl file.
    The optional label can span multiple lines, since BibTeX wraps long
    lines, and can contain braces, e.g., `[DSR{\\etalchar{+}}18]`."""
    keys = set()
    for _match in _RE_BIBITEM.finditer(content):
        idx = _match.end()
        if content.startswith("[", idx):
            depth = 0
            for idx in range(idx, len(content)):
                depth += {"{": 1, "}": -1}.get(content[idx], 0)
                if content[idx] == "]" and depth == 0:
                    break
            idx += 1
        _key = _RE_BIBITEM_KEY.match(content, idx)
        if _key:
            keys.add(_key.group(1))
    return keys

def get_bbl_keys(bbl_file, encoding="utf-8"):
    """Extract citation keys from a .bbl file, auto-detecting the backend."""
    with open(bbl_file, encoding=encoding) as _bbl_file:
        content = _bbl_file.read()
    biblatex_keys = set(re.findall(r"\\entry\{([^}]+)\}", content))
    bibtex_keys = get_bibitem_keys(content)
    if biblatex_keys and not bibtex_keys:
        return biblatex_keys, "biblatex"
    if bibtex_keys and not biblatex_keys:
        return bibtex_keys, "bibtex"
    return biblatex_keys | bibtex_keys, "unknown"


def get_referenced_ids(entry):
    """Return the IDs of all entries that an entry refers to, e.g., the
    parent of a crossref, whose fields the entry inherits."""
    ids = []
    for _key in KEYS_REFERENCE:
        ids.extend([k.strip() for k in entry.get(_key, "").split(",")
                    if k.strip()])
    return ids

def add_referenced_ids(ids, entries):
    """Add the IDs of all entries that the entries with the given IDs refer
    to, recursively. Only IDs of existing entries are added."""
    references = {}
    for entry in entries:
        references.setdefault(entry[KEY_ID], []).extend(get_referenced_ids(entry))
    ids = set(ids)
    stack = list(ids)
    while stack:
        for _ref in references.get(stack.pop(), []):
            if _ref in references and _ref not in ids:
                ids.add(_ref)
                stack.append(_ref)
    return ids


def filter_cited_main(bib_file, bbl_file, verbose=logging.WARN, encoding="utf-8"):
    logging.basicConfig(format="%(asctime)s - [%(levelname)8s]: %(message)s")
    logger = logging.getLogger("filter_cited")
    logger.setLevel(verbose)
    logger.info("Filtering entries of %s using citations from %s", bib_file, bbl_file)
    bib_database = load_bib_file(bib_file, abbr=None, encoding=encoding)
    entries = bib_database.get_entry_list()
    cited_keys, backend = get_bbl_keys(bbl_file, encoding=encoding)
    logger.info("Detected bbl backend: %s", backend)
    logger.info("Found %d cited keys in bbl file", len(cited_keys))
    bib_ids = set(entry.get(KEY_ID) for entry in entries)
    keep_ids = add_referenced_ids(cited_keys, entries)
    referenced = keep_ids - cited_keys
    kept = [entry for entry in entries if entry.get(KEY_ID) in keep_ids]
    unused = bib_ids - keep_ids
    missing = cited_keys - bib_ids
    logger.info("Keeping %d of %d entries", len(kept), len(entries))
    if referenced:
        logger.info("Keeping %d entries that cited entries refer to, e.g., "
                    "with crossref: %s", len(referenced),
                    ", ".join(sorted(referenced)))
    if unused:
        logger.info("Dropping %d uncited entries: %s",
                    len(unused), ", ".join(sorted(unused)))
    if missing:
        logger.warning("%d cited keys are not present in the bib file: %s",
                       len(missing), ", ".join(sorted(missing)))
    return kept
