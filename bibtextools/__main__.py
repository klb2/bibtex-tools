import os.path
import logging

import click

from . import __version__
from .clean_bib_file import clean_bib_file_main
from .combine_bib_files import combine_bib_files_main
from .modernize_bib_file import modernize_bib_main
from .util import write_bib_database

DEFAULT_REMOVE = ["abstract", "annote",
                  "bdsk-url-1",
                  #"comments", "comment",
                  "date-added", "date-modified", 
                  "file",
                  #"keyword", "keywords", 
                  "owner",
                  "timestamp"]


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.group()
@click.pass_context
@click.argument("bib_file", required=True, type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(exists=False))
@click.option("-v", "--verbose", count=True)
@click.option("--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True)
def main(ctx, bib_file, output, verbose):
    ctx.params['verbose'] = max([logging.WARN - 10*verbose, logging.DEBUG])


@main.command()
@click.pass_context
@click.option("-r", "--remove_fields", multiple=True, default=DEFAULT_REMOVE)
@click.option("--replace_ids", is_flag=True, default=False)
@click.option("--arxiv", is_flag=True, default=False)
@click.option("--shield_title", is_flag=True, default=False)
def modernize(ctx, remove_fields, replace_ids, arxiv, shield_title):
    clean_entries = modernize_bib_main(remove_fields=remove_fields,
                                       replace_ids=replace_ids,
                                       arxiv=arxiv,
                                       shield_title=shield_title,
                                       verbose=ctx.parent.params['verbose'],
                                       bib_file=ctx.parent.params['bib_file'])
    return clean_entries

@main.command()
@click.pass_context
@click.option("-a", "--abbr_file", type=click.Path(exists=True, dir_okay=False))
@click.option("-r", "--remove_fields", multiple=True, default=DEFAULT_REMOVE)
@click.option("-u", "--replace_unicode", is_flag=True)
def clean(ctx, abbr_file, remove_fields, replace_unicode):
    clean_entries = clean_bib_file_main(remove_fields=remove_fields,
                                        replace_unicode=replace_unicode,
                                        abbr_file=abbr_file,
                                        verbose=ctx.parent.params['verbose'],
                                        bib_file=ctx.parent.params['bib_file'])
    return clean_entries


@main.result_callback()
@click.pass_context
def save_file(ctx, result, bib_file, output, verbose):
    if output is None:
        _out_dir, _out_base = os.path.split(bib_file)
        output = os.path.join(_out_dir, "{}-{}".format(ctx.invoked_subcommand, _out_base))
    write_bib_database(result, output, encoding='utf-8')
    if ctx.params['verbose'] <= logging.INFO:
        click.echo("Saved {:d} entries to {}".format(len(result), output))

if __name__ == "__main__":
    main()
