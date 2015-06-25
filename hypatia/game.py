# hypatia/game.py
# Lillian Lemmer <lillian.lynn.lemmer@gmail.com>
#
# This module is part of Hypatia and is released under the
# MIT License: http://opensource.org/licenses/MIT

"""Why stuff is drawn; logic flow for the game.

Game logic, game component interaction.

Glues various modules/game components together with behaviors defined
in methods belonging to Game().

Note:
  I have not decided firmly on the approach to take. Expect heavy
  changes in the future.

  Sorry for the poor documentation, I have not devised an actual
  architecture for this particular module. I have not decided
  firmly on the approach to take. Here, I'm sort of imitating
  Flask's app.

"""

import os
import sys

try:
    import ConfigParser as configparser

except ImportError:
    import configparser

import pygame
from pygame.locals import *

from hypatia import tiles
from hypatia import dialog
from hypatia import render
from hypatia import player
from hypatia import sprites
from hypatia import constants

__author__ = "Lillian Lemmer"
__copyright__ = "Copyright 2015, Lillian Lemmer"
__credits__ = ["Lillian Lemmer"]
__license__ = "MIT"
__maintainer__ = "Lillian Lemmer"
__email__ = "lillian.lynn.lemmer@gmail.com"
__status__ = "Development"


class Game(object):
    """Simulates the interaction between game components."""

    def __init__(self, screen=None, scene_name=None, viewport_size=None, dialogbox=None):
        self.screen = screen or render.Screen()
        self.viewport = render.Viewport(viewport_size)
        self.dialogbox = dialogbox or dialog.DialogBox(self.viewport.rect.size)

        # everything has been added, run runtime_setup() on each
        # relevant item
        self.scene = Scene(scene_name)
        self.scene.runtime_setup()
        self.start_loop()

    def handle_input(self):
        """...

        Returns
          bool: returns True if escape was never pressed; returns
            false if escape pressed.

        """
        
        for event in pygame.event.get():

            if event.type == KEYUP:
                self.scene.human_player.walkabout.action = constants.Action.Stand
            
            # need to trap player in a next loop, release when no next
            if event.type == KEYDOWN and event.key == K_SPACE:

                # do until 
                if self.dialogbox.active:
                    self.dialogbox.next()
                else:
                    self.scene.human_player.talk(self.scene.npcs, self.dialogbox)
        
        if self.dialogbox.active:
            
            return True
            
        pressed_keys = pygame.key.get_pressed()
        
        if pressed_keys[K_ESCAPE]:

            return False

        if pressed_keys[K_UP]:
            self.move_player(constants.Direction.Up)

        if pressed_keys[K_RIGHT]:
            self.move_player(constants.Direction.Right)

        if pressed_keys[K_DOWN]:
            self.move_player(constants.Direction.Down)

        if pressed_keys[K_LEFT]:
            self.move_player(constants.Direction.Left)

        return True

    def move_player(self, direction):
        """Modify human player's positional data legally (check
        for collisions).

        Note:
          Will round down to nearest probable step
          if full step is impassable.
          
          Needs to use velocity instead...

        Args:
          direction (constants.Direction): may be one of: Up, Right, Down, Left

        """

        player = self.scene.human_player
        player.walkabout.direction = direction
        planned_movement_in_pixels = (player.walkabout.
                                      speed_in_pixels_per_second)
        adj_speed = self.screen.time_elapsed_milliseconds / 1000.0
        iter_pixels = max([1, int(planned_movement_in_pixels)])

        # test a series of positions
        for pixels in range(iter_pixels, 0, -1):
            # create a rectangle at the new position
            new_topleft_x, new_topleft_y = player.walkabout.topleft_float

            # what's going on here
            if pixels == 2:
                adj_speed = 1

            if direction == constants.Direction.Up:
                new_topleft_y -= pixels * adj_speed
            elif direction == constants.Direction.Right:
                new_topleft_x += pixels * adj_speed
            elif direction == constants.Direction.Down:
                new_topleft_y += pixels * adj_speed
            elif direction == constants.Direction.Left:
                new_topleft_x -= pixels * adj_speed

            destination_rect = pygame.Rect((new_topleft_x, new_topleft_y),
                                           self.scene.human_player.walkabout.size)
            collision_rect = player.walkabout.rect.union(destination_rect)

            if not self.collide_check(collision_rect):
                # we're done, we can move!
                new_topleft = (new_topleft_x, new_topleft_y)
                player.walkabout.action = constants.Action.Walk
                animation = player.walkabout.current_animation()
                player.walkabout.size = animation.getMaxSize()
                player.walkabout.rect = destination_rect
                player.walkabout.topleft_float = new_topleft

                return True

        # never found an applicable destination
        player.walkabout.action = constants.Action.Stand

        return False

    def collide_check(self, rect):
        """Returns True if there are collisions with rect.
        
        """
        
        possible_collisions = self.scene.tilemap.impassable_rects
        
        for npc in self.scene.npcs:
            possible_collisions.append(npc.walkabout.rect)

        return rect.collidelist(possible_collisions) != -1

    def render(self):
        """Drawing behavior for game objects.

        """

        first_tilemap_layer = self.scene.tilemap.layer_images[0]
        self.viewport.center_on(self.scene.human_player.walkabout,
                                first_tilemap_layer.get_rect())
        self.viewport.blit(first_tilemap_layer)
        self.scene.tilemap.blit_layer_animated_tiles(self.viewport, 0)

        # render each npc walkabout
        for npc in self.scene.npcs:
            npc.walkabout.blit(
                               self.viewport.surface,
                               self.viewport.rect.topleft
                              )

        # finally human and rest map layers last
        self.scene.human_player.walkabout.blit(
                                               self.viewport.surface,
                                               self.viewport.rect.topleft
                                             )

        for i, layer in enumerate(self.scene.tilemap.layer_images[1:], 1):
            self.viewport.blit(layer)
            self.scene.tilemap.blit_layer_animated_tiles(self.viewport, i)
            
        self.dialogbox.blit(self.viewport.surface)

    def start_loop(self):

        while self.handle_input():
            self.handle_input()
            self.screen.update(self.viewport.surface)
            self.render()

        pygame.quit()
        sys.exit()


class Scene(object):
    """A map with configuration data/meta, e.g., NPCs.

    Attributes:
      tilemap (hypatia.tiles.Tilemap): --
      player_start_position (tuple): (x, y); two integer tuple
        denoting the starting position for human player.
      human_player (hypatia.player.Player): the human player object.
      npcs (list): a list of hypatia.player.NPC objects

    """

    def __init__(self, scene_name):
        """

        Args:
          scene_name (str): the name of the directory which corresponds
            to the map you want to load from resources/maps.

        """

        scene_directory = os.path.join('resources', 'scenes', scene_name)

        # scene.ini
        scene_ini_path = os.path.join(scene_directory, 'scene.ini')
        scene_ini = configparser.ConfigParser()
        scene_ini.read(scene_ini_path)

        # .. scene data
        # .. should include tilesheet
        tilemap_string_path = os.path.join(scene_directory, 'tilemap.txt')

        with open(tilemap_string_path) as f:
            tilemap_string = f.read()

        self.tilemap = tiles.TileMap.from_string(tilemap_string)

        # .. player start position
        player_start_x = scene_ini.getint('general', 'player_start_x')
        player_start_y = scene_ini.getint('general', 'player_start_y')
        self.player_start_position = (player_start_x, player_start_y)

        # .. create player with player scene data
        hat = sprites.Walkabout('hat')
        human_walkabout = sprites.Walkabout('debug',
                                            position=self.player_start_position,
                                            children=[hat])
        self.human_player = player.Player(walkabout=human_walkabout)

        # npcs.ini
        npcs_ini_path = os.path.join(scene_directory, 'npcs.ini')
        npcs_ini = configparser.ConfigParser()
        npcs_ini.read(npcs_ini_path)

        self.npcs = []

        for npc_name in npcs_ini.sections():
            walkabout_name = npcs_ini.get(npc_name, 'walkabout')
            position_x = npcs_ini.getint(npc_name, 'position_x')
            position_y = npcs_ini.getint(npc_name, 'position_y')
            position = (position_x, position_y)

            npc_walkabout = sprites.Walkabout(walkabout_name,
                                              position=position)

            if npcs_ini.has_option(npc_name, 'say'):
                say_text = npcs_ini.get(npc_name, 'say')
            else:
                say_text = None

            npc = player.Npc(walkabout=npc_walkabout, say_text=say_text)
            self.npcs.append(npc)

    def runtime_setup(self):
        """Initialize al the NPCs, tilemap, etc.

        """

        npcs_to_setup = tuple(npc.walkabout for npc in self.npcs)
        objects_to_setup = (self.tilemap, self.human_player.walkabout,)
        objects_to_setup = objects_to_setup + npcs_to_setup

        for object_to_setup in objects_to_setup + npcs_to_setup:
            object_to_setup.runtime_setup()

