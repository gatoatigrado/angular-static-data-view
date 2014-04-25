# -*- coding: utf-8 -*-
"""Makes a data view page. See the readme."""
import os
import os.path
import random
import shutil
import subprocess
import time

import blessings
import simplejson

from static_html_data_view import command_options
from static_html_data_view.generation_settings import get_generation_settings
from static_html_data_view.generate_index_html import generate_index_html


t = blessings.Terminal()


def generate_data(settings):
    """Generate a template.

    :param settings: GenerationSettings
    """
    out_file = lambda *subpath: os.path.join(settings.out_dir, *subpath)

    # Validate data, if applicable
    validator = settings.special_template_files.get('data_jsonschema.yaml')
    validator and validator.validate(settings.data)

    # Recursively copy anything from the templates directory, create out_dir too.
    shutil.copytree(settings.template_dir, settings.out_dir)

    with open(out_file('data.json'), 'w') as f:
        simplejson.dump(settings.data, f)

    for filename in ['app.js', 'extra.js']:
        if not os.path.isfile(out_file(filename)):
            shutil.copy(os.path.join(settings.system_template_dir, filename), out_file(filename))

    # If templates really want, they can override index.html ... but we advise against it.
    if not os.path.isfile(out_file('index.html')):
        with open(out_file('index.html'), 'w') as f:
            f.write(generate_index_html(settings))


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

    elif not raw_options.no_launch_webserver:
        port = random.randint(7000, 8000)
        print("\n" + t.magenta("Starting web server; press ctrl+c to stop."))
        web_server = subprocess.Popen(['python', '-m', 'SimpleHTTPServer', str(port)], cwd=output_dir)
        time.sleep(0.3)
        assert web_server.poll() is None, "Web server failed."
        if raw_options.launch_browser:
            subprocess.Popen(['open', 'http://localhost:{0}'.format(port)])
        try:
            assert web_server.wait() == 0
        except KeyboardInterrupt:
            time.sleep(0.3)  # let the simplehttpserver's stderr get flushed

    if raw_options.delete_after:
        print("\n" + t.magenta("deleting output..."))
        subprocess.check_call(['rm', '-rv', output_dir])


def main():
    cmdopts = command_options.command_line()
    options, args = cmdopts.parse_args()
    generation_settings = get_generation_settings(options, args, cmdopts.error)
    generate_data(generation_settings)
    post_generation(generation_settings.out_dir, options)


if __name__ == "__main__":
    main()
