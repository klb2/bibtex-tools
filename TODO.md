## TODOs
The following features are planned
* Deal with multiple URLs that are separated by space, e.g., when exporting
  from Mendeley
* Maybe there is an issue when both URL and DOI are provided. Maybe delete URL,
  if DOI is specified
* [Unicode to LaTeX](https://github.com/steog88/bibtexTools)
* IEEE abbreviations could be hardcoded and always replaced
* After fixing duplicates, it needs to be checked again that it did not
  introduce new duplicates
* Unicode support, e.g., when replacing IDs replace unicode characters
* Unify name scheme to `lastName, firstName`. The `bibtexparser.customization`
  module has a function to do that.
