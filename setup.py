try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'IDS Support Tool',
    'author': 'Andreas Happe',
    'url': 'http://www.coretec.at/',
    'download_url': 'http://www.coretec.at',
    'author_email': 'andreashappe@snikt.net',
    'version': '0.1',
    'install_requires': ['nose', 'sqlalchemy', 'future', 'psycopg2'],
    'packages': ['log_importer', 'log_importer.log_import', 'log_importer.data', 'log_importer.log_analyzer'],
    'scripts': [],
    'name': 'log_importer'
}

setup(**config)
