# -*- coding: utf-8 -*-
"""Top-level data generation routine. Called by main.py"""
import os
import os.path
import shutil

import simplejson

from static_html_data_view.generate_index_html import generate_index_html


def _write_file(filename, writer):
    """Abstraction for more easily mocking stuff in tests.

    :param filename: Filename to write to
    :type filename: str
    :param writer: Method which will write to an open FD
    :type writer: fd --> ()
    """
    with open(filename, 'w') as f:
        writer(f)


def generate_data_view(settings, write_file=None):
    """Generate a template.

    :param settings: GenerationSettings
    """
    out_file = lambda *subpath: os.path.join(settings.out_dir, *subpath)
    write_file = write_file or _write_file

    # Validate data, if applicable
    validator = settings.special_template_files.get('data_jsonschema.yaml')
    validator and validator.validate(settings.data)

    # Recursively copy anything from the templates directory, create out_dir too.
    shutil.copytree(settings.template_dir, settings.out_dir)

    write_file(out_file('data.json'), lambda f: simplejson.dump(settings.data, f))

    for filename in ['app.js', 'extra.js']:
        if not os.path.isfile(out_file(filename)):
            shutil.copy(os.path.join(settings.system_template_dir, filename), out_file(filename))

    # If templates really want, they can override index.html ... but we advise against it.
    if not os.path.isfile(out_file('index.html')):
        write_file(
            out_file('index.html'),
            lambda f: f.write(generate_index_html(settings))
        )
