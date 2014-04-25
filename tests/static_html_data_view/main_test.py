# -*- coding: utf-8 -*-
"""Tests for the main methods, including some smoke/integration tests."""
import fileinput

import mock
import testify

from static_html_data_view import main


class MainTest(testify.TestCase):
    @mock.patch.object(fileinput, 'input', return_value=['33\n'])
    @mock.patch.object(main, 'post_generation', lambda *args, **kwargs: None)
    @mock.patch.object(main, 'generate_data')
    def test_arg_parsing(self, generate_data_mock, fileinput_mock):
        main.main(['basic', '-b'])
        ((settings,), _), = generate_data_mock.call_args_list
        assert settings.system_template_dir
        assert settings.template_dir
        testify.assert_equal(settings.data, [33])
