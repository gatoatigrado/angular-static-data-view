# -*- coding: utf-8 -*-
"""Gets the raw options."""
import optparse


def command_line():
    """Gets a command line options instance.

    :rtype: OptionParser
    """
    cmdopts = optparse.OptionParser(usage="%prog make_data_view_page.py <template> <files>")
    cmdopts.add_option(
        "-e",
        action="store_true",
        help="open controller and template in an editor"
    )
    cmdopts.add_option(
        "-s",
        "--single-json-blob",
        action="store_true",
        help="assume input is a single JSON document, rather than lines of JSON"
    )
    cmdopts.add_option(
        "-o",
        "--output-directory",
        help="Output directory (defaults to $template_name-$datetime)"
    )
    cmdopts.add_option(
        "-W",
        "--no-launch-webserver",
        action="store_true",
        help="Don't launch the web server after generation."
    )
    cmdopts.add_option(
        "-b",
        "--launch-browser",
        action="store_true",
        help="Launch web browser. Only makes sense without --no-launch-webserver"
    )
    cmdopts.add_option(
        "-d",
        "--delete-after",
        action="store_true",
        help="Deletes the output after scp (or, in the future, viewing)"
    )
    cmdopts.add_option(
        "--scp-output",
        help="scp the output to a web server"
    )
    return cmdopts
