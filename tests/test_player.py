# This module is part of Hypatia and is released under the
# MIT license: http://opensource.org/licenses/MIT

"""Unit tests for the `hypatia/player.py` code."""

import pytest
from unittest.mock import patch

from hypatia import player


class TestNPC(object):
    """Unit tests for the player.NPC class."""

    def test_inactive_by_default(self):
        """Asserts that NPCs are not active by default."""
        npc = player.NPC()
        assert npc.active is False

    def test_cannot_delete_active_property(self):
        """Asserts that trying to delete the `active` property of an NPC
        raises a TypeError.

        """
        npc = player.NPC()
        with pytest.raises(TypeError):
            del npc.active

    def test_cannot_modify_activation_count_property(self):
        """Asserts that trying to directly modify or delete the
        `activation_count` property of an NPC raises a TypeError.

        """
        npc = player.NPC()
        with pytest.raises(TypeError):
            npc.activation_count += 1
        with pytest.raises(TypeError):
            del npc.activation_count

    def test_cannot_exceed_activation_limit(self):
        """Asserts that we cannot activate an NPC more times than allowed by
        its activation limit property.

        """
        npc = player.NPC()
        npc.activation_limit = 0
        with pytest.raises(player.CannotActivateNPC):
            npc.active = True

    def test_setting_active_invokes_methods(self):
        """Asserts that setting the `active` property of an NPC to True will
        invoke its on_activation() method, and likewise, setting the
        property to False invokes the on_deactivation() method.

        """
        with patch.object(player.NPC, "on_activation") as mock_method:
            npc = player.NPC()
            npc.active = True
            mock_method.assert_called_once_with()

        with patch.object(player.NPC, "on_deactivation") as mock_method:
            npc = player.NPC()
            npc.active = False
            mock_method.assert_called_once_with()
