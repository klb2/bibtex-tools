import os.path
import argparse
import logging

from .modernize_bib_file import modernize_bib_main
from .clean_bib_file import clean_bib_file_main
from .combine_bib_files import combine_bib_files_main
from .util import write_bib_database

DEFAULT_REMOVE = ["abstract", "annote",
                  "bdsk-url-1",
                  #"comments", "comment",
                  "date-added", "date-modified", 
                  "file",
                  #"keyword", "keywords", 
                  "owner",
                  "timestamp"]

def get_arg_parser():
    parser = argparse.ArgumentParser(prog="bibtex-tools")
    subparsers = parser.add_subparsers(help="Possible sub commands", 
                                       required=True,
                                       dest="command")
    #parser.add_argument("-o", "--output", help="Output file for the new bib entries. If not specified, it will be the input file with a 'modern-' prefix.")
    #parser.add_argument("bib_file")
    parser_modern = subparsers.add_parser("modernize",
            help="Modernize a bib file. This replaces fields by the proper BibLaTeX syntax and removes unwanted fields. It also does some cleaning steps")
    parser_modern.add_argument("-r", "--remove_fields", nargs="*",
                        default=DEFAULT_REMOVE,
                        help="Name of fields that should be removed for the clean bib file. By default, this is 'abstract', 'annote', 'file', 'keyword'. Leave empty to not delete any fields")
    parser_modern.add_argument("--replace_ids", action="store_true",
                        help="If this is set, the IDs of the bib entries are replaced by a fixed scheme")
    parser_modern.add_argument("--arxiv", action="store_true",
                        help="If this is set, the primaryClasses are downloaded for arXiv preprints. Requires an eprint field in the entry")
    parser_modern.add_argument("--shield_title", action="store_true",
                        help="If this is set, the title field will be surrounded by curly brackets.")
    parser_modern.add_argument("--iso4", action="store_true",
                        help="If this is set, the journal titles will be abbreviated according to the ISO4 standard.")
    parser_modern.add_argument("--force", action="store_true", help="Force the automatic removal of duplicate entries (the shorter one will be removed) and skip the interactive prompt.")
    parser_modern.add_argument("-v", "--verbose", action="count", default=0, help="Verbosity level. -v is info and -vv is debug")
    parser_modern.add_argument("-o", "--output", help="Output file for the new bib entries. If not specified, it will be the input file with a 'clean-' prefix.")
    parser_modern.add_argument("bib_file")

    parser_clean = subparsers.add_parser("clean", help="Clean a bib file. This can remove unwanted fields, checks for duplicates, replaces abbreviations, and converts unicode characters.")
    parser_clean.add_argument("-a", "--abbr_file",
                              help="Bib-file that contains abbreviations")
    parser_clean.add_argument("-r", "--remove_fields", nargs="*",
                        default=DEFAULT_REMOVE,
                        help="Name of fields that should be removed for the clean bib file. By default, this is 'abstract', 'annote', 'file', 'keyword'. Leave empty to not delete any fields")
    parser_clean.add_argument("-u", "--replace_unicode", action="store_true", help='Replace unicode characters by the LaTeX syntax, e.g., ä --> {\\"a}')
    parser_clean.add_argument("--force", action="store_true", help="Force the automatic removal of duplicate entries (the shorter one will be removed) and skip the interactive prompt.")
    parser_clean.add_argument("-v", "--verbose", action="count", default=0, help="Verbosity level. -v is info and -vv is debug")
    parser_clean.add_argument("-o", "--output", help="Output file for the new bib entries. If not specified, it will be the input file with a 'clean-' prefix.")
    parser_clean.add_argument("bib_file")

    parser_combine = subparsers.add_parser("combine", help="Combine multiple bib files into a single one.")
    #parser_combine.add_argument("-a", "--abbr_file", help="Bib-file that contains abbreviations")
    parser_combine.add_argument("-v", "--verbose", action="count", default=0, help="Verbosity level. -v is info and -vv is debug")
    parser_combine.add_argument("--allow_duplicates", action="store_true", help="If this option is passed, the IDs of the bib items remain untouched. This leads to duplicate IDs if the same key is used in multiple files. Note that duplicate entries (by content) will still be removed.")
    parser_combine.add_argument("--force", action="store_true", help="Force the automatic removal of duplicate entries with the same citation (the shorter one will be removed) and skip the interactive prompt.")
    parser_combine.add_argument("-o", "--output", help="Output file for the new bib entries. If not specified, it will be the input file with a 'clean-' prefix.")
    parser_combine.add_argument("bib_files", nargs="+")
    return parser


def parse_args(parser):
    args = vars(parser.parse_args())
    args['verbose'] = max([logging.WARN - 10*args['verbose'], logging.DEBUG])
    return args

def main():
    parser = get_arg_parser()
    args = parse_args(parser)
    logger = logging.getLogger(__name__)
    logger.setLevel(args['verbose'])
    command = args.pop("command")
    output = args.pop("output")
    if command == "modernize":
        clean_entries = modernize_bib_main(**args)
    elif command == "clean":
        clean_entries = clean_bib_file_main(**args)
    elif command == "combine":
        clean_entries = combine_bib_files_main(**args)
    if output is None:
        if command == "combine":
            _bib_file_name = args['bib_files'][0]
        else:
            _bib_file_name = args['bib_file']
        _out_dir, _out_base = os.path.split(_bib_file_name)
        output = os.path.join(_out_dir, "{}-{}".format(command, _out_base))
    logger.info("Saving %d cleaned entries to: %s", len(clean_entries), output)
    write_bib_database(clean_entries, output, encoding="utf-8")
    logger.info("Successfully saved new file.")

if __name__ == "__main__":
    main()
