#!/bin/sh
#
# This script is STRONGLY recommended for verifying the quality and
# functionality of your contribution.
#
# This script can be ran as a pre-push git hook; please see the etc/
# directory in this project's root.
#
# Not used for Travis CI, because this launches the demo game.
#
# Also checks the validity of the markdown-to-PyPI-rst conversion
# performed on README.md. This is done in order to provide PyPi
# with a nice package page/read me.
#
# CAVEAT: If you get an error about --no-cache-dir,
# you need to upgrade pip.
#
# This script does the following:
#   1. Uninstall the current hypatia_engine Python package
#   2. convert README.md to PKG-INFO (rst)
#   3. Validate PKG-INFO, if it doesn't validate it won't be
#      formatted on PyPi
#   4. Install the local repo's package for Hypatia as user,
#      using pip and setup.py.
#   5. Remove the PKG-INFO file (we were only validating it)
#   6. Use py.test to check for PEP8 rule violations, to
#      doctest all docstrings, provide a test coverage
#      report and pipe all of this information to MORE
#   7. The demo game.py will be launched, utilizing the
#      freshly installed Hypatia package from this local
#      repository.
#
# If the optional environment variable $HYPATIA_PYTHON_VERSION is
# present then the script will append its value to the `python` and
# `pip` commands.  For example, if $HYPATIA_PYTHON_VERSION equals
# "3.5" then the script will use the programs...
#
#     1. python3.5
#     2. pip3.5
#
# ...making it possible to control which version of Python Hypatia
# uses for testing the code, as some platforms and/or developers have
# versions of Python with slightly different names or have multiple
# versions installed.  The optional $HYPATIA_PYTHON_VERSION variable
# gives those developers a way to tell Hypatia which version to use
# without having to directly modify this script.

PIP="pip${HYPATIA_PYTHON_VERSION}"
PYTHON="python${HYPATIA_PYTHON_VERSION}"
PAGER="${PAGER:=more}"

"$PIP" uninstall hypatia_engine -y
pandoc README.md -t rst -o PKG-INFO
"$PYTHON" setup.py check -r -s
"$PIP" install --user --no-cache-dir --upgrade --force-reinstall .
rm PKG-INFO
py.test tests --pep8 --doctest-modules hypatia -v --cov-report term-missing --cov=hypatia | "$PAGER"
cd demo
"$PYTHON" game.py
cd ..
