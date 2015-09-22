# This module is part of Hypatia and is released under the
# MIT license: http://opensource.org/licenses/MIT

"""py.test unit testing for hypatia/actor.py

Run py.test on this module to assert hypatia.actor
is completely functional.

"""

import os

import pygame
import pytest

from hypatia import actor
from hypatia import physics
from hypatia import constants
from hypatia import sprites

try:
    os.chdir('demo')
except OSError:
    pass


class TestActor(object):
    """A grouping of tests for the actor.Actor class.

    """

    def test_blah(self):
        pass


def test_no_response():
    """Test the exception class.

    Also See:
        * actor.NoResponse
        * actor.NoResponseReason

    """

    # If the response reason is invalid a typeerror should be raised
    with pytest.raises(TypeError):

        raise actor.NoResponse(2)

    # Give NoResponse a valid reason and see if it raises NoResponse
    with pytest.raises(actor.NoResponse):

            raise actor.NoResponse(actor.NoResponseReason.no_say_text)

    # Make sure the reason attribute is accessible and is set
    # to the supplied and valid reason.
    try:

        raise actor.NoResponse(actor.NoResponseReason.no_say_text)

    except actor.NoResponse as no_response:

        assert no_response.reason == actor.NoResponseReason.no_say_text


def test_actor():
    """Test actor.Actor class.

    This is bad and outdated and bad.

    """

    walkabout = sprites.Walkabout('debug')
    velocity = physics.Velocity(10, 10)
    an_actor = actor.Actor(walkabout=walkabout,
                           say_text='Hello, world!',
                           velocity=velocity)
