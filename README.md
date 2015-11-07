# Hypatia 0.3.4 (alpha)

![Hypatia 0.3.4](http://hypatia-engine.github.io/assets/logotype-dark.png)

[![GitHub license](https://img.shields.io/github/license/hypatia-engine/hypatia.svg?style=flat-square)](https://raw.githubusercontent.com/hypatia-engine/hypatia/master/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/hypatia_engine.svg?style=flat-square)](https://pypi.python.org/pypi/hypatia_engine/)
[![Travis](https://img.shields.io/travis/hypatia-engine/hypatia.svg?style=flat-square)](https://travis-ci.org/hypatia-engine/hypatia)
[![Coveralls](https://img.shields.io/coveralls/lillian-lemmer/hypatia.svg?style=flat-square)](https://coveralls.io/r/lillian-lemmer/hypatia)
[![Code Climate](https://img.shields.io/codeclimate/github/lillian-lemmer/hypatia.svg?style=flat-square)](https://codeclimate.com/github/lillian-lemmer/hypatia)
[![PyPI Popularity](https://img.shields.io/pypi/dm/hypatia_engine.svg?style=flat-square)](https://pypi.python.org/pypi/hypatia_engine/)
[![Bountysource](https://img.shields.io/bountysource/team/hypatia/activity.svg?style=flat-square)](https://www.bountysource.com/teams/hypatia)
[![Donate with Paypal](https://img.shields.io/badge/paypal-donate-ff69b4.svg?style=flat-square)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=YFHB5TMMXMNT6)
[![Donate with Patreon](https://img.shields.io/badge/patreon-donate%20monthly-ff69b4.svg?style=flat-square)](https://www.patreon.com/lilylemmer)

Make 2D action adventure games. For programmers and nonprogrammers alike.

Create games like [_Legend of Zelda: Oracle of Ages_ and _Oracle of Seasons_](http://en.wikipedia.org/wiki/The_Legend_of_Zelda:_Oracle_of_Seasons_and_Oracle_of_Ages).

The included demo game (`demo/game.py`) in action:

![The demo game in action.](http://hypatia-engine.github.io/assets/demo.gif)

## What makes this project special?

  * Each release tested in FreeBSD, Linux, and Windows
  * Built and tested in FreeBSD first
  * A labor of love,
    [permissively (MIT) licensed](https://raw.githubusercontent.com/hypatia-engine/hypatia/master/LICENSE),
    meaning you Hypatia for commercial or non-commercial purposes and
    not worry about legalese--it's really free for any purpose without
    strings attached.

## Resources

  * [Platform-specific packages](http://hypatia-engine.github.io/get.html)
  * [Hypatia Wiki](http://hypatia-engine.github.io/wiki/)
    (great resource for nonprogrammers, too!)
  * [The official Hypatia website](http://hypatia-engine.github.io/)
  * Official support chat:
    [#hypatia on Freenode (webui!)](http://webchat.freenode.net/?channels=hypatia)
  * [Hypatia Engine Slack team chat](https://hypatia-engine.slack.com/)
  * You can contact the author via email: lillian.lynn.lemmer@gmail.com,
    [@LilyLemmer](https:/twitter.com/LilyLemmer) on Twitter.

To know your way around the project, I strongly recommend reading the
[CONTRIBUTING.md](https://github.com/lillian-lemmer/hypatia/blob/master/CONTRIBUTING.md)
file. It covers everything you need to know about contributing to
Hypatia, as well as navigating the project.

## Getting Started

If you have just one version of Python installed, simply use:

```shell
./scripts/bootstrap
```

Otherwise, follow these two instructions:

  1. Install Pygame (platform-specific)
  2. In the repository root, run `pip install --user .`

### Checkout the Demo

```shell
$ cd demo
$ python game.py
```

### Platform-Specific Pre-requisite Instructions

Installing Pygame on various platforms. I assume you have Python
installed and know how to use `pip`.

#### FreeBSD, DragonflyBSD, PC-BSD, etc.

The easiest thing to do is use Python 2.7. You can simply:

```shell
pkg install py27-game
```

#### OpenBSD

```shell
pkg_add pygame
```

#### Debian, Ubuntu

```shell
sudo apt-get install python-pygame
```

#### Mac OS X

Install pygame through Homebrew. You may want to install
Python through Homebrew as well.

```shell
# install homebrew
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
# install pygame through homebrew
brew install homebrew/python/pygame
```

#### Windows

For Python 2.x I recommend using
[Pygame's official Windows installers](http://www.pygame.org/download.shtml).

If you're using Python 3.x, I recommend using Christoph Gohlke's
_unofficial_ Pygame binaries. Make sure to download the `whl` specific
to your Python version and architecture (win32 vs win_amd64). To
install the `whl` do the following in command prompt (in the directory
containing the `whl):

```shell
pip install wheel
pip install pygame-*.whl
```
