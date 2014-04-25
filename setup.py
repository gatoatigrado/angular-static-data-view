from setuptools import find_packages
from setuptools import setup


setup(
    name="static_html_data_view",
    version="0.1.0",
    provides=["static_html_data_view"],
    author="gatoatigrado",
    author_email="gatoatigrado@gmail.com",
    url="https://github.com/gatoatigrado/angular-static-data-view",
    description='visualize small amounts of data with angular',
    install_requires=[
        'blessings',
        'jsonschema',
        'pyyaml',
        'simplejson',
    ],
    packages=find_packages(exclude=['tests*']),
    entry_points={
        'console_scripts': [
            'make_data_view_page=static_html_data_view.main:main',
        ],
    },
)
