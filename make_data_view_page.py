# -*- coding: utf-8 -*-
"""Makes a data view page. See the readme."""
import datetime
import fileinput
import os
import os.path
import random
import shutil
import subprocess
import time
from collections import namedtuple

import blessings
import simplejson

from data_view import command_options

t = blessings.Terminal()

mod_path = os.path.abspath(os.path.dirname(__file__))

# Resolve module templates -- see usage in parse_cmdline()
exists_or_none = lambda f: (os.path.exists(f) and f) or None
resolve_template_path = lambda *subpath: (
    exists_or_none(os.path.join(mod_path, 'templates', *subpath)) or
    exists_or_none(os.path.join(os.path.expanduser("~/.config/data_view_templates"), *subpath))
)

# various util stuff
date_for_directory_name = lambda: datetime.datetime.now().isoformat().replace(':', '.')


# Settings related to template generation
GenerationSettings = namedtuple("GenerationSettings", [
    "template_dir",
    "out_dir",
    "data",
])


def parse_cmdline_and_load_data():
    """What it says -- parses the command line, loads input data [from stdin or files].

    :rtype: (GenerationSettings, OptionParser)
    """
    cmdopts = command_options.command_line()
    options, args = cmdopts.parse_args()

    assert len(args) >= 1
    template_name = args[0]
    template_dir = resolve_template_path(template_name)
    data = fileinput.input(files=args[1:], openhook=fileinput.hook_compressed)
    data = simplejson.loads(''.join(data)) if options.single_json_blob else map(simplejson.loads, data)

    # check that the template / appropriate template files exist.
    if not template_dir:
        cmdopts.error(
            "Couldn't find your template among global templates "
            "or in ~/.config/data_view_templates"
        )
    elif not all(os.path.isfile(os.path.join(template_dir, f)) for f in ['view.html', 'controller.js']):
        cmdopts.error(
            "All templates must have a view.html and controller.js file."
        )

    return (
        GenerationSettings(
            template_dir=template_dir,
            out_dir=(
                options.output_directory or
                '{0}-{1}'.format(template_name, date_for_directory_name())
            ),
            data=data,
        ),
        options
    )


def validate_data(settings):
    schema_file = os.path.join(settings.template_dir, 'data_jsonschema.yaml')
    if os.path.isfile(schema_file):
        import yaml
        import jsonschema.validators
        with open(schema_file) as f:
            validator = jsonschema.validators.Draft4Validator(yaml.safe_load(f))
        validator.validate(settings.data)


def generate_data(settings):
    """Generate a template.

    :param settings: GenerationSettings
    """
    out_file = lambda *subpath: os.path.join(settings.out_dir, *subpath)

    validate_data(settings)

    shutil.copytree(settings.template_dir, settings.out_dir)  # will create the dir too.
    for filename in ['index.html', 'app.js', 'extra.js']:
        if not os.path.isfile(out_file(filename)):
            shutil.copy(os.path.join(mod_path, 'static', filename), out_file(filename))
    with open(out_file('data.json'), 'w') as f:
        simplejson.dump(settings.data, f)


def post_generation(output_dir, raw_options):
    """Launch any helpful processes post-generation. Blocks until these processes
    are done.

    :type raw_options:
        OptionParser, result of command_options.command_line().parse_args()
    """
    subprocess.check_call(['tree', '--noreport', output_dir])

    if raw_options.scp_output:
        print("\n" + t.magenta("scp'ing output..."))
        subprocess.check_call(['scp', '-Cr', output_dir, raw_options.scp_output])
        if raw_options.delete_after:
            print("\n" + t.magenta("deleting output..."))
            subprocess.check_call(['rm', '-rv', output_dir])

    elif not raw_options.no_launch_webserver:
        port = random.randint(7000, 8000)
        web_server = subprocess.Popen(['python', '-m', 'SimpleHTTPServer', str(port)], cwd=output_dir)
        time.sleep(0.5)
        assert web_server.poll() is None, "Web server failed."
        if raw_options.launch_browser:
            subprocess.Popen(['open', 'http://localhost:{0}'.format(port)])
        assert web_server.wait() == 0


def main():
    generation_settings, opts = parse_cmdline_and_load_data()
    generate_data(generation_settings)
    post_generation(generation_settings.out_dir, opts)


if __name__ == "__main__":
    main()
