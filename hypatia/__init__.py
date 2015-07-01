"""This module contains all of the important meta-information for
Hypatia such as the author's name, the copyright and license, status,
and so on.

"""

__author__     = "Lillian Lemmer"
__copyright__  = "Copyright 2015 Lillian Lemmer"
__credits__    = ["Lillian Lemmer"]
__license__    = "MIT"
__maintainer__ = __author__
__site__       = "http://lillian-lemmer.github.io/hypatia/"
__email__      = "lillian.lynn.lemmer@gmail.com"
__status__     = "Development"



class Version:
    """A represntation of Hypatia's current version.

    This class contains integer fields for the major, minor, and patch
    version numbers, respectively.  This is useful for comparison
    within code if it becomes necessary to have code behave
    differently based on the version, e.g. for backwards
    compatibility.  The class also supports str() which converts an
    instance into a human-readable string, e.g. '0.2.8'.

    Public Properties:

    * major
    * minor
    * patch

    """
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self):
        return "%d.%d.%d" % (self.major, self.minor, self.patch)


# str(__version__) will produce a string like "0.2.8"
__version__ = Version(0, 2, 8)



__contributors__ = [
    "Lillian Lemmer",
    "Brian Houston Morrow",
    "Eric James Michael Ritz"
]
