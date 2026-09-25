## TODOs
The following features are planned
* Deal with multiple URLs that are separated by space, e.g., when exporting
  from Mendeley
* Maybe there is an issue when both URL and DOI are provided. Maybe delete URL,
  if DOI is specified
* IEEE abbreviations could be hardcoded and always replaced
* Known issue in `modernize` function: When authors are specified in the form
  `author={First Name {with multiple last names} and Second Author}`, the
  restructuring does not work properly.
* Add a `convert` subcommand that allows conversion between multiple formats
  like BibTeX, YAML, JSON, ...
* Add `_` as a character that needs to be shielded in math mode
