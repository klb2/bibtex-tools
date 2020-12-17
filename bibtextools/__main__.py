import argparse
import logging

from .clean_bib_file import clean_bib_main

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("bib_file")
    parser.add_argument("-r", "--remove_fields", nargs="*",
                        default=["abstract", "annote", "file", "keyword"],
                        help="Name of fields that should be removed for the clean bib file. By default, this is 'abstract', 'annote', 'file', 'keyword'. Leave empty to not delete any fields")
    parser.add_argument("--replace_ids", action="store_true",
                        help="If this is set, the IDs of the bib entries are replaced by a fixed scheme")
    parser.add_argument("--arxiv", action="store_true",
                        help="If this is set, the primaryClasses are downloaded for arXiv preprints. Requires an eprint field in the entry")
    parser.add_argument("-o", "--output", help="Output file for the clean bib entries. If not specified, it will be the input file with a 'clean-' prefix.")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Verbosity level. -v is info and -vv is debug")
    return parser


def parse_args(parser):
    args = vars(parser.parse_args())
    args['verbose'] = max([logging.WARN - 10*args['verbose'], logging.DEBUG])
    clean_bib_main(**args)

def main():
    parser = get_args()
    parse_args(parser)

if __name__ == "__main__":
    main()
