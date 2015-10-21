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
    'packages': ['victims-db-builder'],
    'package_dir': {'': 'src'},
    'scripts': ['src/victims-db-builder/processor.py'],
    'install_requires': ['requests>=2.8.1', 'pyyaml>=3.11']
}

setup(**config)
