# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## Unreleased
### Added
- In the removal of duplicate entries, typing `0` will continue the process
  without deletig any of the two entries.

## [0.5.0] - 2024-10-15
### Added
- Add `KEY_EDITOR` and `KEY_BOOKTITLE` keywords to constants
- Add `clean_bib_file.get_duplicate_entries` function that returns duplicate
  entries based on their similar titles, authors, and other information
- Add `clean_bib_file.remove_duplicate_entries` function that removes duplicate
  entries based on the content (similar titles, authors, ...). Additionally,
  this function is applied to all main functions after loading the bib files.
- Add new `--force` option for the CLI commands, which skip the interactive
  prompt for removing duplicate citations.

### Changed
- Rename the `clean_bib_file.get_duplicates` function to
  `clean_bib_file.get_duplicate_ids`.
- Rename the `clean_bib_file.replace_duplicates` function to
  `clean_bib_file.replace_duplicate_ids`.
- Move `modernize_bib_file.getnames()` to `util.getnames()`



## [0.4.0] - 2024-02-14
### Added
- Added function to abbreviate journal names based on the ISO4 standard using
  the `pyiso4` implementation as part of the `modernize` command. 

### Changed
- Update packaging structure and metadata from old `setup.py` to
  `pyproject.toml`
- Change minimum Python version requirement to 3.8 due to the pyiso4 dependency



## [0.3.1] - 2022-02-17
### Added
- A completely refactored command line interface using the `click` library is
  added. This will replace the current CLI in a future version.

### Fixed
- Fixed a bug in getting author names when shielded umlauts were already
  present.



## [0.3.0] - 2021-11-29
### Added
- It is now possible to change the sorting of the entries when writing to a
  file
- Added the `shield_title` argument for modernizing the title field, which
  allows adding/removing curly brackets around the title field.
  The argument can be used by setting the `--shield_title` flag in the
  `modernize` command.

### Changed
- The fields `keyword` and `keywords` do not get removed by default
- Surrounding curly brackets in the title field are removed by default. Use the
  `--shield_title` argument to avoid this.



## [0.2.2] - 2021-01-22
### Fixed
- Already converted unicode symbols are not touched when cleaning unicode 
  characters.
- Improve author name cleaning in `modernize` subcommand. Names that are
  shielded by `{}` are now split into first and last names respecting the
  grouping.



## [0.2.1] - 2021-01-11
### Fixed
- Acronyms that are already shielded by `{}` will not be shielded again when
  modernizing a bib file.



## [0.2.0] - 2021-01-04
### Added
- Added subcommand functionality. Available subcommands are `clean`, `combine`,
  and `modernize`.
- Added `clean` functionality, that e.g., allows renaming duplicate IDs.
- Added `combine` functionality that allows combining multiple bib files into a
  single one.
- The minimum required version of Python is 3.7.



## [0.1.1] - 2020-12-17
### Fixed
- Fix issue when using `--replace_ids` with author names that already contain
  unicode characters in ASCII LaTeX format, e.g., \"{O} instead of Ö.



## [0.1.0] - 2020-12-17
### Added
- Script to clean bib files with the following features
- Page field is cleaned (en-dash `--` is used to separate numbers)
- Month field is cleaned (numbers are used instead of the old `jan` format)
- Eprint field is cleaned ("arXiv:" is stripped)
- Title field is cleaned (acronyms are shielded with curly brackets)
- Support for adding `primaryClass` field for arXiv articles
- Entry-IDs can be replaced with the scheme `<Author><year><firstWordOfTitle>`
