from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='pyworks',
    version='0.9.0',  # Required
    description='An Task framework',
    long_description=long_description,
    url='https://github.com/pylots/pyworks',
    author='Rene Nejsum, __PYLOTS__',  # Optional
    author_email='rene@pylots.com',  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='actors concurrency development',
    packages=find_packages(exclude=['example', 'docs', 'venv', 'web', 'db']),
    install_requires=['jinja2'], #['flask', 'flask_restful', 'markupsafe', 'waitress', 'flask_login'],
    entry_points={  # Optional
        'console_scripts': [
            'pyworks=pyworks.cli:commandline',
        ],
    },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/pylots/pyworks/issues',
        'Source': 'https://github.com/pylots/pyworks/',
    },
)
