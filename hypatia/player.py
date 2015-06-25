"""Interactive map entities/players!

Note:
  Could even be something like a sign! Or the human player.
  
"""

from hypatia import dialog
from hypatia import sprites
from hypatia import constants


class Player(object):

    def __init__(self, walkabout=None):
        self.walkabout = walkabout or sprites.Walkabout()

    def talk(self, npcs, dialogbox):
        """Attempt to talk in current direction.
        
        """
        
        # get the current direction, check a bit in front with a rect
        # to talk to npc if collide
        facing = self.walkabout.direction
        
        if facing is constants.Direction.Up:
            disposition = (0, -1)
        elif facing is constants.Direction.Right:
            disposition = (1, 0)
        elif facing is constants.Direction.Down:
            disposition = (0, 1)
        elif facing is constants.Direction.Left:
            disposition = (-1, 0)

        talk_rect = self.walkabout.rect.copy()
        talk_rect.move_ip(disposition)
        
        for npc in npcs:
            
            if npc.walkabout.rect.colliderect(talk_rect):
                npc.say(facing, dialogbox)


class Npc(Player):

    def __init__(self, *args, **kwargs):
        self.say_text = kwargs.pop('say_text', None)

        super(Npc, self).__init__(*args, **kwargs)

    def say(self, at_direction, dialogbox):
        facing = {
                  constants.Direction.Up: constants.Direction.Down,
                  constants.Direction.Right: constants.Direction.Left,
                  constants.Direction.Left: constants.Direction.Right,
                  constants.Direction.Down: constants.Direction.Up
                 }[at_direction]
        self.walkabout.direction = facing
        
        if self.say_text:
            dialogbox.set_message(self.say_text)

