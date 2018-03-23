from setuptools import setup, find_packages

setup(
    name='captive protal',
    version='0.01',
    description=('captive protal with an SMS auth for the Ubiquity UniFi controller'),
    long_description=__doc__,
    packages=['captive'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['alembic', 'Flask', 'Flask-Login', 'Flask-Migrate', 'Flask-SQLAlchemy', 'Flask-WTF',
    'Jinja2', 'Mako', 'pyunifi', 'requests', 'SQLAlchemy', 'urllib3', 'Werkzeug', 'WTForms' ],
    entry_points={ 'flask.commands': [ 'db=flask_migrate.cli:db' ], },
)
