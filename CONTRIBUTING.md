# Contributing to Hypatia

This document is for Python devs to read before making contributions
to Hypatia. When you make a _pull request_ it is assumed you have
read this document.

Before you continue, you need to read `LICENSE`, `README.md`,
and `CODE-OF-CONDUCT`.

Hypatia stricly enforces the `CODE-OF-CONDUCT.md`. We strive for a
safe, healthy social environment for all women, whether cis or trans.

Please communicate with our lovely team:

  * IRC: Freenode #hypatia
  * Twitter: @hypatia_engine
  * Email: hypatia.engine@gmail.com

Lily, project mommy:

  * Email: lillian.lynn.lemmer@gmail.com
  * Twitter: @LilyLemmer (you can *really* get to know her)

You may ask Lillian for access to the private team chat. When you
email `lillian.lynn.lemmer@gmail.com` be sure to mention why
you're interested, a tiny bit about yourself, and maybe a Twitter,
blog, or something!

## Quick Info

  * Branch from, pull request to develop
  * Use descriptive branch names
  * We're strict about documentation (docstrings, commit messages, comments)
  * Use test.sh to test before you commit!
  * You'll probably want to pip install --user requirements/testing.txt
  * This repo's etc/ directory contains additional/optional tools to assist contributors
  * Before anything is merged to `develop` you need at least one person to approve the
    change in a pull request. The convention for showing approval for a commit is giving
    your thumbs-up :+1:, hopefully with a comment.
  * Complete repository review is required to merge back to `master`, this means a pull
    request requiring the approval and input of (hopefully) all contributors. Also,
    changes must first be tested in all supported platforms.

## Git

### Creating a New Branch

All new branches **must** fork from `master`, e.g. `git checkout -b your-new-feature-or-fix master`.

#### Rationale

The `master` branch at all times represents the most stable version of Hypatia.  All new branches must fork from `master` so that they begin with the most stable foundation possible.  This helps cut down on the number of bugs and problems that can arise from forking a branch from a less stable branch, e.g. an existing feature branch; the new branch will inherit any problems or conflicts of that branch.  By forking all branches from `master` those branches are less likely to inherit any problems than if they forked from anywhere else.

### General Practices

* Try to avoid large/huge commits
* Try to avoid imlementing multiple concepts in one commit
* A branch should only implement what its name describes, e.g., "add-display-settings-and-tools"

### Git Messages

Commit messages **must** begin with single line summarizing the patch, followed by a blank line, and then the rest of the message.  The blank line is mandatory because without the output of many Git commands become messy to read, e.g. `git shortlog`.

Commit messages must be as explanatory as possible.  Any developer should be able to understand *why* a change was made just by reading the commit message for that change.  This means that commit messages that cotain only `"Fixes a bug"` or `"Updates to sprite code"` are unacceptable.  When writing a commit message ask yourself, *"Why is this change necessary?"*  Your message must answer that question.  [Here is an example commit](https://github.com/hypatia-engine/hypatia/commit/fdbfc5f3e62eb4f5d04ca23f5705e4e97a5e89bf) which answers that question.

If your commit is a bug-fix then try to find the commit which introduced the bug and reference that in your message.  The preferred format is `first eight digits of the SHA-1 (The Commit's First Line)`.  [Here is an example](https://github.com/hypatia-engine/hypatia/commit/b52c3345ae8e312017c2a1cf21793fdbc63b2493) demonstrating how to refer to previous commits.  Note well that GitHub automatically creates links to commits you reference in this way.

If your commit relates to a GitHub issue then reference that issue in the message by writing `GitHub-Issue: #NNN` where `NNN` is the issue number.  [Here is an example](https://github.com/hypatia-engine/hypatia/commit/04d64aa1c76d1958d934c9d64e72a6928ab6466f) of such references.  Again, note well that GitHub turns these references into links.  The threads for those issues will also receive a link back to the commit.

### Merging Branches

#### Getting Reviews and Testing

A branch is not acceptable for merging until one of the "core contributors" has reviewed and tested the branch.  In this context "core contributors" refers to the people with read/write permissions on the official repository.  At this time of writing those people are:

- Lillian Lemmer
- Alice Jenkinson
- Eric James Michael Ritz

#### Merging Branches in Preparation for Updating Master

All branches deemed acceptable for merging into Hypatia are first merged into the `develop` branch.  The `develop` branch is always forked from `master`.  It represents "the next version of `master`", i.e. what `master` will become after all merging and integration testing is complete.  These are the steps that the "core contributors" must follow for merging branches in preparation for updating `master`.

1. Create `develop` if it does not already exist, i.e. `git branch develop master`.

2. `git checkout develop`

3. For each branch `foo` that is acceptable for merging, first run `git checkout develop` to switch to the `develop` branch.  If the branch `foo` contains only a single commit: `git cherry-pick -s foo`.  If the branch `foo` contains more than one commit: `git merge --no-ff --edit foo`.  The purpose of these two commands is to add metadata to the commits indicating that the core contributor performing the merge has "signed off" on the branch, i.e. that contributor takes full responsibility for having tested and reviewed the branch in question.

4. `git push origin develop` so that everyone may test the proposed changes.

##### Rationale for Merging Process

Using `git cherry-pick -s foo` for a branch that contains only one commit avoids creating a merge commit, which is unnecessary noise for such branches.  If it is necessary to revert a branch in the future then we only need a single commit to revert.  For branches containing only one commit we do not need a merge commit to revert; we can simply revert the commit itself.  For branches containing more than one commit, `git merge --no-ff --edit foo` guarantees that we will have a merge commit that we can use with `git revert` at any point in the future to "unhook" that branch from the repository, thus undoing all of its changes.  The `-s` flag for `git cherry-pick` and the `--edit` flag for `git merge` gives the core contributors the chance to sign-off on the branch, indicating they have reviewed and tested the branch and that they accept responsibility for the quality of that branch meeting the standards of the project.

#### Merging All Changes Into Master

Once all branches deemed acceptable for merging are in `develop` then all developers should `git checkout develop` and test the changes as much as possible.  Once satisfied with their quality then one of the core contributors updates `master` with the following commands:

    git checkout master
    git merge --ff-only develop

##### Rationale for `--ff-only`

A "fast-forward" merge in Git is a merge which **does not** create a merge commit.  Using `--ff-only` will reject the merge if it cannot be done without creating a merge commit.  The reason this flag is mandatory is that if we cannot fast-forward merge `develop` into `master` then that indicates there are merge conflicts which are either unresolved or need to be re-reviewed.  To put it another way, `git merge --ff-only develop` guarantees that Git can update `master` "cleanly" by simply updating `master` to point to the same commit as `develop`.

#### Tagging Master for a New Release

After merging `develop` into `master` it may be time to tag `master` as a new version for release.  The commands for this are:

    git checkout master
    git tag -s v0.4.0

Here `v0.4.0` is only an example tag name.  *Only Lillian can run these commands.*  That is because the `-s` flag to `git tag` will sign the tag with her GPG key, which other developers can use to verify the validity and authenticity of the tag.  As the project lead of Hypatia, Lillian is the only person with authority to use `git tag -s`.  **No other developers must ever use `git tag -s` under any circumstances.**  However, using `git tag` without `-s` is fine, which developers can use to create local "lightweight" tags if needed to help development.

#### Pushing Updates to Master and Preparing for the Next Development Cycle

- `git fetch origin --prune`
- `git checkout master`
- `git push origin master --tags`
- `git branch -d develop && git branch develop master`

The command `git branch --merged` will show all branches merged into `master`.  For each such branch:

- `git branch -d that-branch` **Note:** `-D` will be necessary for branches merged via `git cherry-pick -s`.
- `git push origin --delete that-branch`

## General Documentation Rules

  * Always explain what everything is and how it works, to the best of your understanding!
  * Amazing docstrings are a must!
  * Always use gender neutral pronouns in all documentation, including code comments, e.g., they, them, their.
 
## Code Style

  * [PEP8 Style Guide](https://www.python.org/dev/peps/pep-0008/)

### Docstrings

You are required to write _amazing docstrings_. The docstring convention used is [Google Style Docstrings](http://sphinxcontrib-napoleon.readthedocs.org/en/latest/example_google.html).

All of the following must have *thorough docstrings*:

  * Modules
  * Functions
  * Classes
  * Methods (yes, even __init__)

A *thorough docstring*:

  * Has more than a brief description
  * Justifies the existence of whatever its describing
  * A module-level docstring with a section for constants, where the module's constants are thoroughly explained.
  * If for a function or method, describes possible return value, and describes arguments with more than a brief description. Try including doctest examples in your argument elaboration.
  * Has a doctest

Use four spaces to indent within docstrings:

```python
def dummy(dumb):
    """One-line description.

    Elaborative description.

    Args:
        dumb (int): A dumb number. Remember we
            said we use four spaces to indent?

    """

    pass
```

The following code snippet exemplifies everything described in this section (_Docstrings_):

```python
class Anchor(object):
    """A coordinate on a surface which is used for pinning to another
    surface Anchor. Used when attempting to afix one surface to
    another, lining up their corresponding anchors.
    Attributes:
        x (int): x-axis coordinate on a surface to place anchor at
        y (int): y-axis coordinate on a surface to place anchor at
    Example:
        >>> anchor = Anchor(5, 3)
        >>> anchor.x
        5
        >>> anchor.y
        3
        >>> coordinate_tuple = (1, 2)
        >>> anchor = Anchor(*coordinate_tuple)
        >>> anchor.x
        1
        >>> anchor.y
        2
    """

    def __init__(self, x, y):
        """Create an Anchor using two integers to
        represent this Anchor's coordinate.
        Args:
            x (int): X-axis position of the supplied
                coordinate in pixels.
            y (int): Y-axis position of the supplied
                coordinate in pixels.
        """

        self.x = x
        self.y = y

    def __repr__(self):
        """
        Example:
            >>> anchor = Anchor(1, 2)
            >>> print(anchor)
            <Anchor at (1, 2)>
        """

        return "<Anchor at (%d, %d)>" % (self.x, self.y)

    def __add__(self, coordinates):
        """Adds X-Y coordinates to the coordinates of an Anchor.
        Args:
            coordinates (Union[Anchor|Tuple[int, int]]):
                The X-Y coordinates to add to the coordinates
                of the current Anchor.  The argument may be
                another Anchor object or tuple of two integers.
        Returns:
            Anchor: A new Anchor with the coordinates of
                the first and second added together.
        Raises:
            NotImplemented: If `coordinates` is not an `Anchor`
                or a 2-tuple of integers.
        Example:
            >>> anchor_a = Anchor(4, 1)
            >>> anchor_b = Anchor(2, 0)
            >>> anchor_a + anchor_b
            <Anchor at (6, 1)>
            >>> coordinate_tuple = (10, 20)
            >>> anchor_a + coordinate_tuple
            <Anchor at (14, 21)>
            >>> coordinate_tuple + anchor_a
            <Anchor at (14, 21)>
            >>> anchor_a + 1.5 # doctest: +SKIP
            Traceback (most recent call last):
            TypeError: 'float' object is not subscriptable
        """

        if isinstance(coordinates, Anchor):

            return Anchor(self.x + coordinates.x,
                          self.y + coordinates.y)

        elif type(coordinates[0]) == int and type(coordinates[1]) == int:

            return Anchor(self.x + coordinates[0],
                          self.y + coordinates[1])

        else:

            raise NotImplementedError(coordinates)

    def __radd__(self, coordinates):
        """Implements addition when the Anchor is the right-hand operand.
        See Also: `Anchor.__add__()`
        Example:
            >>> coordinates = (1, 2)
            >>> anchor = Anchor(100, 200)
            >>> coordinates + anchor
            <Anchor at (101, 202)>
        """

        return self + coordinates

    def __sub__(self, coordinates):
        """Subtracts the given X-Y coordinates from the Anchor.
        Args:
            coordinates (Union[Anchor|Tuple[int, int]]):
                The X-Y coordinates to subtract from the coordinates
                of the current Anchor.  The argument may be another
                Anchor object or tuple of two integers.
        Returns:
            Anchor: A new Anchor with the coordinates of
                the second subtracted from the first.
        Raises:
            NotImplemented: If `coordinates` is not an `Anchor`
                or a 2-tuple of integers.
        Example:
            >>> anchor_a = Anchor(4, 1)
            >>> anchor_b = Anchor(2, 0)
            >>> anchor_a - anchor_b
            <Anchor at (2, 1)>
            >>> coordinate_tuple = (3, 0)
            >>> anchor_a - coordinate_tuple
            <Anchor at (1, 1)>
            >>> coordinate_tuple - anchor_b
            <Anchor at (1, 0)>
            >>> anchor_a - 3.2 # doctest: +SKIP
            Traceback (most recent call last):
            TypeError: 'float' object is not subscriptable
        """

        if isinstance(coordinates, Anchor):

            return Anchor(self.x - coordinates.x,
                          self.y - coordinates.y)

        elif type(coordinates[0]) == int and type(coordinates[1]) == int:

            return Anchor(self.x - coordinates[0],
                          self.y - coordinates[1])

        else:

            raise NotImplemented

    def __rsub__(self, coordinates):
        """Implements subtraction when the Anchor is the right-hand operand.
        Example:
            >>> coordinates = (100, 200)
            >>> anchor = Anchor(1, 1)
            >>> coordinates - anchor
            <Anchor at (99, 199)>
        See Also: `Anchor.__sub__()`
        """
        # The naive implementation would be...
        #
        #     return self - coordinates
        #
        # ...but that produces the wrong result because subtraction is
        # not commutative.  We also cannot write...
        #
        #     return coordinates - self
        #
        # ...because then we're invoking this method again, i.e. we
        # create a never-ending loop.
        #
        # To deal with this problem we take advantage of the fact that
        # the following mathematical expressions are equivalent for
        # natural numbers:
        #
        #     x - y
        #     (-x) + y
        #
        # Therefore we create a new `Anchor` which is the inverse of
        # the `self`, i.e. the `x` in the example above, and then we
        # *add* the coordinates (`y`) to that, which gives us the
        # correct result.

        return (self * -1) + coordinates

    def __mul__(self, multiplier):
        """Multiplies the X-Y coordinates of an Anchor by an integer.
        Args:
            multiplier (int): The number to multiply to each coordinate.
        Returns:
            Anchor: A new Anchor object with X-Y coordinates multiplied
                by the `multiplier` argument.
        Raises:
            NotImplemented: If `multiplier` is not an integer.
        Example:
            >>> anchor = Anchor(3, 5)
            >>> anchor * -1
            <Anchor at (-3, -5)>
            >>> anchor * 0
            <Anchor at (0, 0)>
            >>> 2 * anchor
            <Anchor at (6, 10)>
            >>> anchor * 1.5 # doctest: +SKIP
            Traceback (most recent call last):
            TypeError: exceptions must derive from BaseException
        """

        if type(multiplier) == int:

            return Anchor(self.x * multiplier, self.y * multiplier)

        else:

            raise NotImplemented

    def __rmul__(self, multiplier):
        """Allows the Anchor to be on the right-hand of multiplication.
        See Also: `Anchor.__mul__()`
        Example:
            >>> 10 * Anchor(1, 2)
            <Anchor at (10, 20)>
            >>> 2.5 * Anchor(0, 0) # doctest: +SKIP
            Traceback (most recent call last):
            TypeError: exceptions must derive from BaseException
        """

        return self * multiplier

    def as_tuple(self):
        """Represent this anchors's (x, y)
        coordinates as a Python tuple.
        Returns:
            tuple(int, int): (x, y) coordinate tuple
                of this Anchor.
        """

        return (self.x, self.y)
```

### Doctests

Doctests are *required* in docstrings for the following, as to provide a proof-of-concept:

  * Classes
  * Methods
  * Functions

Here are some relevant resources on doctests:

  * [Official Python guide on doctests](https://docs.python.org/2/library/doctest.html)
  * [A wonderful, more thorough guide on doctests](http://pymotw.com/2/doctest/)

Our doctests are verified by Travis CI. You can avoid embarassment by running the `test.sh` supplied in the repo to test your changes.

### Whitespace

Whitespace is important. You use whitespace to make stuff stand out. You use whitespace to set relation. See: [The Law of Proximity](http://study.com/academy/lesson/law-of-proximity-examples-lesson-quiz.html).

The following effect major events to logic, and thus require whitespace (blank line) above and below:

  * `return`
  * `break`
  * `continue`
  * `yield`
  * `raise`


```python
if x == 2:

    continue

elif x == 3:

    return None

elif x == 4:
    x += 1
elif x == 6:

    break

elif x == 10:

    raise Exception("Whoops!")
```

It's keen to add a blank line below if/else/elif blocks which exceed one line, as to separate it from the next else/elif block. For example:

```python
if user_input == EAT_TACO:
    player.eat(taco)
    player.satisfied = True

elif user_input == PLAY_GAME:
    player.play_game(castlevania)
    player.satisfied = True

elif user_input == CHOOSE_TO_BE_SATISFIED:
    player.satisfied = True
else:
    player.satisfied = False
```

Always add a blank line above and below the terminating quote for the docstring. For example:

```python
def dummy():
    """Fake description of function.

    """

    pass


def another_dummy():
    """A fake description of this other
    fake function.

    Only designed for you to understand
    code style guidelines.

    """

    pass
```

The following must have a blank line above:

  * `except`: when the respective try block exceeds one line
  * `else`, `elif`: when the previous `else`, `elif`, or `if` block exceeded one line

Example of what must have a blank line above:

```python
try:
    d = {}
    d['lol no such key']

except KeyError:
    print("what a horrible example")

if x == 3:
    x += 5
    y -= 3
    a = x - y

elif x == 5:
    x -= 4
elif x == 6:
    x += 8
    y -= 9

else:
    x = 5
```

## tests

* Hypatia uses pytest for automated testing. To set up your Hypatia repository for testing, run the following:

  ```
  cd /path/to/hypatia-repository
  pip install -r requirements/testing.txt
  ```

  You can now run the tests by running `test.sh`.

* Reference `tests/test_tiles.py` for an example on how to structure your tests. See [official pytest usage examples](http://pytest.org/latest/example) for more generic samples. 
  * Avoid creating classes in your tests.
  * The following try/except block is needed:

    ```
    try:
        os.chdir('demo')
    except OSError:
        pass
    ```

## File and Directory Notes

### distrib.sh

This script is used for distributing A NEW RELEASE to PyPi.

### demo/

This directory hosts `game.py`, which is a demo of Hypatia. It also hosts the demo's editable resources.

### docs/

Sphinx docs source. Use the custom `make-sphinx.sh` to build the sphinx documentation from the docstrings.

The *built* Sphinx docs are published to the official Hypatia website, at the following URI: http://lillian-lemmer.github.io/hypatia/api

### etc/

*OPTIONAL* configurations/configuration scripts, helper files, etc. Worth checking out! Has a `objecttypes.xml` for Tiled editor!

### hypatia/

The actual Python package source.

### media/

Media, namely pictures, officially related to Hypatia as a project, e.g., logos, icons.

### requirements/

The requirements files installable by `pip`. Notes on the files:

|Requirements File|You'd want to use if...                        |
|-----------------|-----------------------------------------------|
|testing.txt      |You want to test and/or contribute to the code!|
|travis.txt       |NEVER, this is for Travis CI                   |
|distrib.txt      |Distributing new release on PyPi               |

### tests/

Unit tests for py.test and Travis Continuous Integration. These files are for assuring Hypatia's API remains consistent, reproducible, functional, etc. They are in part what determines build success/fail according to Travis CI. See our `build` badge.

See also: `test.sh`, it's the official script to run when testing any changes.
