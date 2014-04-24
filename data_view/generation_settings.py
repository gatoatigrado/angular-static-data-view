# -*- coding: utf-8 -*-
"""Generates the index.html file."""
import datetime
import fileinput
import os
import os.path
from collections import namedtuple

import jsonschema
import simplejson
import yaml

mod_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

exists_or_none = lambda f: (os.path.exists(f) and f) or None
resolve_template_path = lambda *subpath: (
    exists_or_none(os.path.join(mod_path, 'templates', *subpath)) or
    exists_or_none(os.path.join(os.path.expanduser("~/.config/data_view_templates"), *subpath))
)

date_for_directory_name = lambda: datetime.datetime.now().isoformat().replace(':', '.')


# Settings related to template generation
GenerationSettings = namedtuple("GenerationSettings", [
    "system_template_dir",
    "template_dir",
    "out_dir",
    "data",
    "special_template_files",  # loaded files from SPECIAL_TEMPLATE_FILES
])


# filename --> (required, loader)
SPECIAL_TEMPLATE_FILES = {
    'view.html': (True, None),
    'controller.js': (True, None),
    'data_jsonschema.yaml': (False, lambda f: jsonschema.Draft4Validator(yaml.safe_load(f))),
    'js_includes.txt': (False, lambda f: tuple(url.strip() for url in f)),
}


SYSTEM_TEMPLATE_DIR = os.path.join(mod_path, 'static')
assert os.path.isdir(SYSTEM_TEMPLATE_DIR)


def get_generation_settings(options, args, error_fcn):
    """What it says -- parses the command line, loads input data [from stdin or files].

    :param options: Result of cmdopts.parse_args()
    :param args: Result of cmdopts.parse_args()
    :param error_fcn: Function to raise an error (usually, cmdopts.error)
    :rtype: GenerationSettings
    """
    if not args:
        error_fcn("At least one argument (the template name) is required.")

    template_name = args[0]
    template_dir = resolve_template_path(template_name)
    data = fileinput.input(files=args[1:], openhook=fileinput.hook_compressed)
    data = (
        simplejson.loads(''.join(data))
        if options.single_json_blob
        else map(simplejson.loads, data)
    )

    # check that the template / appropriate template files exist.
    if not template_dir:
        cmdopts.error(
            "Couldn't find your template among global templates "
            "or in ~/.config/data_view_templates"
        )

    special_template_files = {}
    for filename, (required, loader) in SPECIAL_TEMPLATE_FILES.iteritems():
        if os.path.isfile(os.path.join(template_dir, filename)):
            if loader:
                with open(os.path.join(template_dir, filename)) as f:
                    special_template_files[filename] = loader(f)
        elif required:
            error_fcn("Required template file {0} was not found".format(filename))

    return GenerationSettings(
        system_template_dir=SYSTEM_TEMPLATE_DIR,
        template_dir=template_dir,
        out_dir=(
            options.output_directory or
            '{0}-{1}'.format(template_name, date_for_directory_name())
        ),
        data=data,
        special_template_files=special_template_files,
    )
