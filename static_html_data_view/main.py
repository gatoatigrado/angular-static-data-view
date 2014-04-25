# -*- coding: utf-8 -*-
"""Makes a data view page. See the readme."""
import random
import subprocess
import time

import blessings

from static_html_data_view import command_options
from static_html_data_view.generation_settings import get_generation_settings
from static_html_data_view.generate_data_view import generate_data_view


t = blessings.Terminal()


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
        web_server = subprocess.Popen(
            ['python', '-m', 'SimpleHTTPServer', str(port)], cwd=output_dir
        )
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


def main(args=None):
    cmdopts = command_options.command_line()
    options, args = cmdopts.parse_args(args=args)
    generation_settings = get_generation_settings(options, args, cmdopts.error)
    generate_data_view(generation_settings)
    post_generation(generation_settings.out_dir, options)


if __name__ == "__main__":
    main()
