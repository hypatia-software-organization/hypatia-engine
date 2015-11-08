# Windows Test Script
#
# Using "Git Bash"
#
# This script has been tested/created on Windows 10.
#
# test.sh is more comprehensive, but this is a script
# I slapped together for fixing errors related to
# Windows.

read -p "Press [Enter] to uninstall then install hypatia_engine..."
# uninstall
py -2 -m pip uninstall hypatia_engine -y
py -3 -m pip uninstall hypatia_engine -y
# install
py -2 -m pip install --user --no-cache-dir -r requirements/python2.txt .
py -3 -m pip install --user --no-cache-dir -r requirements/base.txt .

# RUN THE DEMO
cd demo

read -p "Press [Enter] to test game.py in Python 2..."
py -2 game.py

read -p "Press [Enter] to test game.py in Python 3..."
py -3 game.py

cd ..
