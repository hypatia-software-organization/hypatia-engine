#!/bin/sh
#
# Hypatia installation script for Ubuntu.
#
# Installs the following:
#
#   1. Python 2.7
#   2. Packages python-pygame and python-pip.
#   3. Required packages through pip as the normal user.

sudo apt-get install python2.7 python2.7-dev python2.7-doc python2.7-dbg
sudo apt-get install python-pygame python-pip
pip install --user -r requirements.txt .

