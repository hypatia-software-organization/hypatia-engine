#!/bin/sh
#
# Create API documentation using Sphinx:
#
#     http://sphinx-doc.org/
#
# If the $BROWSER environment variable is set then the script will use
# that to open the documentation locally.  If the variable does not
# exist then the script falls back to using Firefox.
#
######################################################################

BROWSER="${BROWSER:=firefox}"

# Delete existing documentation.  First, however, we change to the
# `docs/` directory.  Ninety-nine percent of the time we will already
# be in that directory when running this script.  But there are two
# `build/` directories: on at the top level and one as a sub-directory
# of `docs/`, thus we change directories to be sure we delete the
# correct `build/` directory.

cd "$(git rev-parse --show-toplevel)/docs"

if [ -d "./build" ]; then
    rm ./build -rf
fi

# Build the documentation.

sphinx-apidoc -f -o . ../hypatia
sphinx-build . build

# Open locally if the build worked.  We give a full `file://` URI to
# our browser because some browsers will incorrectly interpret it as a
# URL such as `http://build/index.html`, which can also happen (less
# likely) depending on local DNS settings.  Using a `file://` URI
# avoids both of these problems.

if [ -e "./build/index.html" ]; then
    "$BROWSER" "file://$(git rev-parse --show-toplevel)/build/index.html"
fi
