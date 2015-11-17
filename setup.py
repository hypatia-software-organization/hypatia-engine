#!/usr/bin/env python

"""Hypatia package installer.

Distributing:

  $ setup.py sdist bdist_wheel
  $ twine upload dist/hypatia_engine-0.2.3.tar.gz dist/hypatia_engine-0.2.3*.whl
  $ rm -rf dist

  You'll need the wheel, twine package for bdist_wheel. Don't forget
  to clear your dist when finished.

Installing:
  `pip install .` in the project root. This script detects the
  python version and builds the install_requires accordingly.

  Does not install pygame. See `README.md`.

"""

import sys
from setuptools import setup
from distutils.version import StrictVersion


# Build the list of packages required according to Python version
install_requires = ['Pillow>=2']

# x.y.z
python_version = StrictVersion('.'.join(str(n) for n in sys.version_info[:3]))

# the `enum` package is a backport of Python 3.5 enum,
# we only want it in earlier versions of python
if python_version < StrictVersion('3.5'):
    install_requires.append('enum34')

exec(open('hypatia/__init__.py').read())
setup(name='hypatia_engine',
      packages=['hypatia'],
      version=__version__,
      description='2D action adventure game engine',
      setup_requires=['setuptools-markdown'],
      # pygame isn't on pypi
      # TODO: i should maybe also specifiy Pillow<4
      install_requires=install_requires,
      long_description_markdown_filename='README.md',
      author='Lillian Lemmer',
      author_email='lillian.lynn.lemmer@gmail.com',
      url='http://hypatia-engine.github.io/hypatia',
      download_url = 'https://github.com/hypatia-engine/hypatia/releases/tag/' + __version__,
      license='MIT',
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.4',
                   'Operating System :: Microsoft :: Windows :: Windows 7',
                   'Operating System :: Microsoft :: Windows :: Windows Vista',
                   'Operating System :: Microsoft :: Windows :: Windows XP',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX :: BSD :: FreeBSD',
                   'Operating System :: POSIX :: Linux',
                   'Topic :: Games/Entertainment :: Role-Playing',
                   'Topic :: Software Development :: Libraries :: pygame',
                  ],
      keywords=('games gaming development sprites adventure game tilemap '
                'tilesheet zelda gamedev 2d')
    )

