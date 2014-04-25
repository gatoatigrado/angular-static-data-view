# -*- coding: utf-8 -*-
"""Generates the index.html file."""


TEMPLATE = r'''
<!DOCTYPE html>
<html>
<head>
    <title>Data viewer</title>
    <script
        type="text/javascript"
        src="https://ajax.googleapis.com/ajax/libs/angularjs/1.2.15/angular.min.js"></script>
    {extra_js_includes}
    <script type="text/javascript" src="extra.js"></script>
    <script type="text/javascript" src="app.js"></script>
    <script type="text/javascript" src="controller.js"></script>
</head>
<body ng-app='app' ng-controller="TopLevelController">
    <ng-include src="'view.html'">
    </ng-include>
</body>
</html>
'''


def generate_index_html(settings):
    """Generates the index.html

    :param settings: GenerationSettings
    """
    return TEMPLATE.format(
        extra_js_includes='\n    '.join(
            r'<script type="text/javascript" src="{url}"></script>'.format(url=url)
            for url in settings.special_template_files.get('js_includes.txt', ())
        )
    )
