#!/bin/sh
#
# This script installs the tools developers need for testing Hypatia.
# Developers must have either `pip` or `pip3` installed.  If both are
# installed then `pip3` is given preference under the assumption that
# the developer prefers to use Python 3.

PIP=$(which pip3)
PIP=${PIP:=$(which pip)}

"$PIP" install pytest

# Depending on which version of `pip` we used above we may have one of
# two possible names for `py.test`.  So here we check for them and set
# the most appropriate one.
PYTEST=$(which py.test)
PYTEST=${PYTEST:=$(which py.test-2.7)}

# Run `py.test --version`, creating no output.  All we are looking for
# is a successful exit code to indicate that the installation worked.
"$PYTEST" --version 1>/dev/null 2>&1

if [ "$?" != "0" ]; then
    echo "Error: Could not install and/or run py.test";
    exit 1;
fi
