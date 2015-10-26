try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'victims-db-builder',
    'description': 'Victims Database Builder',
    'author': ['Jason Shepherd', 'Summer Long'],
    'author_email': 'jason@jasonshepherd.net',
    'url': 'https://github.com/jasinner/victims-db-builder',
    'download_url': 'https://github.com/jasinner/victims-db-builder',
    'version': '1.0',
    'license': 'AGPL',
    'packages': ['victims_db_builder'],
    'scripts': ['victims_db_builder/processor.py'],
    'install_requires': ['requests>=2.8.1', 'pyyaml>=3.11'],
    'tests_require': ['nose>=1.3.7']
}

setup(**config)
