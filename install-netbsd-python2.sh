#!/bin/sh
# Hypatia installation script for NetBSD.
#
# Tested on NetBSD 7.0_RC1. SH.

# Ensure PKG_PATH is set prior to running this script (of the form PKG_PATH=ftp://ftp.netbsd.org/pub/pkgsrc/packages/NetBSD/$arch/$release-number/All/)
# $arch can be obtained with uname -m. $release-number in practice can vary but should match the major NetBSD version.

su root -c 'pkg_add python27 py27-pip py27-game'
./install-base-python2.sh

