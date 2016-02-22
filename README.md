# Hypatia 0.3.6 (alpha)

[![GitHub license](https://img.shields.io/github/license/hypatia-software-org/hypatia-engine.svg?style=flat-square)](https://raw.githubusercontent.com/hypatia-software-org/hypatia-engine/master/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/hypatia_engine.svg?style=flat-square)](https://pypi.python.org/pypi/hypatia_engine/)
[![Travis](https://img.shields.io/travis/hypatia-software-organization/hypatia-engine.svg?style=flat-square)](https://travis-ci.org/hypatia-software-organization/hypatia-engine)
[![Code Climate](https://img.shields.io/codeclimate/github/lillian-lemmer/hypatia.svg?style=flat-square)](https://codeclimate.com/github/hypatia-software-organization/hypatia-engine)
[![PyPI Popularity](https://img.shields.io/pypi/dm/hypatia_engine.svg?style=flat-square)](https://pypi.python.org/pypi/hypatia_engine/)
[![Bountysource](https://img.shields.io/bountysource/team/hypatia-engine/activity.svg?style=flat-square)](https://www.bountysource.com/teams/hypatia-software-org)
[![Donate with Paypal](https://img.shields.io/badge/paypal-donate-ff69b4.svg?style=flat-square)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ZU5EVKVY2DX2S)

Make 2D action adventure games. For programmers and nonprogrammers alike.

Create games like
[_Legend of Zelda: Oracle of Ages_ and _Oracle of Seasons_](http://en.wikipedia.org/wiki/The_Legend_of_Zelda:_Oracle_of_Seasons_and_Oracle_of_Ages).

The included demo game (`demo/game.py`) in action:

![The demo game in action.](https://enginedothypatiadotsoftware.files.wordpress.com/2016/01/demo-2015-11-07-1.gif)

## What makes this project special?

  * Each release tested in FreeBSD, Mac OS X, Linux, and Windows
  * Built and tested in FreeBSD first
  * A labor of love,
    [permissively (MIT) licensed](./LICENSE),
    meaning you Hypatia for commercial or non-commercial purposes and
    not worry about legalese--it's really free for any purpose without
    strings attached.

Hypatia stricly enforces the `CODE-OF-CONDUCT.md`. We strive for a
safe, healthy social environment for all women, whether
[cis](https://en.wikipedia.org/wiki/Cisgender) or trans.

Trans women have access to mentorships, funding, team chat,
and more! For more information please see the
[Hypatia Software Organization website](http://hypatia.software).

## Resources

  * [Hypatia Software Organization](http://hypatia.software): The
    organization which made this fine product.
  * [Platform-specific packages](http://hypatia-engine.github.io/get.html)
  * [Hypatia Wiki](http://hypatia-engine.github.io/wiki/)
    (great resource for nonprogrammers, too!)
  * [The official Hypatia website](http://engine.hypatia.software)
  * Official IRC support chat:
    [#hypatia on Freenode (webui!)](http://webchat.freenode.net/?channels=hypatia)
  * You can contact the author via email: lillian.lynn.lemmer@gmail.com,
    [@LilyLemmer](https:/twitter.com/LilyLemmer) on Twitter.

To know your way around the project, I strongly recommend reading the
[CONTRIBUTING.md](./CONTRIBUTING.md)
file. It covers everything you need to know about contributing to
Hypatia, as well as navigating the project.

## Getting Started

If you have just one version of Python installed, simply use:

```shell
./scripts/bootstrap
```

Otherwise, if you want to install for a
specific version of Python, use something like:

```shell
python3.3 scripts/bootstrap
```

If the bootstrap fails, you can try to install yourself:

  1. Install Pygame (platform-specific). Installing Pygame is
     a different process on various systems. See the
     *Installing Pygame* section below.
  2. `pip install --user .`

### Checkout the Demo

```shell
$ cd demo
$ python game.py
```

### Installing Pygame

**You can skip this section if the bootstrap worked for you.**

Installing Pygame on various platforms. I assume you have Python
installed and know how to use `pip`.

#### FreeBSD, DragonflyBSD, PC-BSD, etc.

The easiest thing to do is use Python 2.7. You can simply:

```shell
sudo pkg install py27-game
```

#### OpenBSD

```shell
sudo pkg_add pygame
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
*unofficial* Pygame binaries. Make sure to download the `whl` specific
to your Python version and architecture (win32 vs win_amd64). To
install the `whl` do the following in command prompt (in the directory
containing the `whl`):

```shell
pip install wheel
pip install pygame-*.whl
```
