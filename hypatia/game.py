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

import io
import os
import sys
import traceback
import xml.etree.ElementTree as ET

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
from hypatia import physics
from hypatia import resources
from hypatia import constants
from hypatia import exceptions
from hypatia import controllers

class Game(object):
    def __init__(self, vfs):
        """The base game object. This links all the components together,
        and is automatically instantiated when Hypatia is loaded with your
        game.

        Args:
          vfs (hypatia.vfs.VFS): The game's virtual file system.
        """

        self.running = True
        self.vfs = vfs

        # load engine default config, then game config, then user config
        self.config = configparser.ConfigParser()
        self.config.readfp(io.BytesIO(constants.DEFAULT_CONFIG))
        self.config.readfp(self.vfs.open("game.ini"))

        self.stages = []

        pygame.init()
        self.clock = pygame.time.Clock()
        self.ms_elapsed = 0

        displayinfo = pygame.display.Info()
        self.physical_size = (displayinfo.current_w, displayinfo.current_h)

        self.update_screen_size()

    def update_screen_size(self):
        screen_size = self.config.get('display', 'screen_size')
        self.screen_size = [int(i) for i in screen_size.split('x')]

        window_size = self.config.get('display', 'window_size')
        self.window_size = [int(i) for i in window_size.split('x')]

        self.fullscreen = self.config.getboolean('display', 'fullscreen')
        self.scaleup = self.config.getboolean('display', 'scaleup')
        self.max_fps = self.config.getint('display', 'maxfps') 

        # set up display itself
        screenres = self.screen_size
        flags = DOUBLEBUF

        if self.fullscreen:
            self.fullscreen = True
            screenres = self.physical_size
            flags = FULLSCREEN | DOUBLEBUF

        elif self.scaleup:
            screenres = self.window_size

        self.screen = pygame.display.set_mode(screenres, flags)

    def update(self):
        if len(self.stages) > 0:
            try:
                self.stages[-1].update()

            except Exception as e:
                self.stage_jump(ExceptionStage)

            surface = self.stages[-1].surface

        else:
            surface = pygame.Surface(self.screen_size)
            surface.fill((51, 51, 51))

        if self.fullscreen:
            surface = pygame.transform.scale(surface, self.physical_size)
        elif self.scaleup:
            surface = pygame.transform.scale(surface, self.window_size)

        self.screen.blit(surface, (0, 0))
        pygame.display.flip()

        self.ms_elapsed = self.clock.tick(self.max_fps)

    def handle_events(self):
        for event in pygame.event.get():
            if len(self.stages) > 0:
                try:
                    self.stages[-1].handle_event(event)

                except:
                    self.stage_jump(ExceptionStage)                    

            if event.type == QUIT: 
                self.running = False 

    def stage_jump(self, cls, *args):
        for i in self.stages:
            i.shutdown()

        c = cls(self, *args)
        c.startup()
        self.stages = [c]

    def stage_push(self, cls, *args):
        if len(self.stages) > 0:
            self.stages[-1].suspend()

        c = cls(self, *args) 
        c.startup()
        self.stages.append(c)

    def stage_pop(self):
        if len(self.stages) > 0:
            self.stages[-1].shutdown()
            return self.stages.pop()

    def main_loop(self):
        while self.running:
            self.handle_events()
            self.update()

class Stage(object):
    def __init__(self, parent):
        self.parent = parent
        self.surface = pygame.Surface(parent.screen_size)

    def startup(self):
        """Perform stage startup.
        """

        pass

    def shutdown(self):
        """Perform scene shutdown. Called before the stage is removed.
        """

        pass

    def suspend(self):
        """Suspend scene.
        """

        pass

    def update(self):
        """Update the stage's surface. Upon resume from suspend, unsuspend
        everything in here, too.
        """

        pass

    def handle_event(self, event):
        """Handle a single pygame event for this stage.
        """

        pass

class ExceptionStage(Stage):
    def startup(self):
        self.renderables = []
        font = pygame.font.SysFont("dejavusans,sans", 18)

        excinfo = io.BytesIO()
        traceback.print_exc(limit=10, file=excinfo)
        excinfo = excinfo.getvalue().decode('utf-8')
        print(excinfo)

        ypos = 8
        for i in excinfo.splitlines():
            c = font.render(i, True, (0, 0, 0))
            self.renderables.append((c, (8, ypos)))
            ypos += c.get_rect().height + 3

    def update(self):
        super(ExceptionStage, self).update()
        self.surface.fill((159, 201, 235))

        for i in self.renderables:
            self.surface.blit(*i)

class Scene(object):
    """A map with configuration data/meta, e.g., NPCs.

    Attributes:
      tilemap (hypatia.tiles.Tilemap): --
      player_start_position (tuple): (x, y); two integer tuple
        denoting the starting position for human player.
      human_player (hypatia.player.Player): the human player object.
      npcs (list): a list of hypatia.player.NPC objects

    Notes:
        Should have methods for managing npcs, e.g., add/remove.

    """

    def __init__(self, tilemap, player_start_position,
                 human_player, npcs=None):
        """
        Args:
            tilemap (tiles.TileMap): --
            player_start_position (tuple): x, y pixel coordinates
                for the human player's starting position.
            human_player (players.HumanPlayer): --
            npcs (List[players.Npc]): --
            npc_sprite_group (pygame.sprite.Group): --

        """

        self.tilemap = tilemap

        self.player_start_position = player_start_position
        self.human_player = human_player

        self.npcs = npcs or []

        npc_walkabouts = [n.walkabout for n in self.npcs]
        self.npc_sprite_group = pygame.sprite.Group(*npc_walkabouts)

    @staticmethod
    def create_human_player(start_position):
        """Currently mostly scaffolding for creating/loading the
        human character into the scene.

        Args:
            start_position (tuple): x, y pixel coordinates
                for the human player's starting position.

        Returns:
            player.HumanPlayer: --

        """

        # .. create player with player scene data
        hat = sprites.Walkabout('hat')
        human_walkabout = sprites.Walkabout('debug',
                                            position=start_position,
                                            children=[hat])
        velocity = physics.Velocity(20, 20)
        human_player = player.HumanPlayer(walkabout=human_walkabout,
                                          velocity=velocity)

        return human_player

    def to_tmx_resource(self, tmx_name):
        """Scaffolding.

        """

        pass

    @classmethod
    def from_tmx_resource(cls, tmx_name):
        """Create a scene from a Tiled editor TMX file in
        the scenes resource directory.

        Returns:
            Scene: A scene created using all compatible
                data from designated TMX file.

        """

        file_path = os.path.join('resources', 'scenes', tmx_name + '.tmx')
        tmx = TMX(file_path)
        human_player = cls.create_human_player(tmx.player_start_position)

        return Scene(
                     tilemap=tmx.tilemap,
                     player_start_position=tmx.player_start_position,
                     human_player=human_player,
                     npcs=tmx.npcs
                    )

    @classmethod
    def from_resource(self, scene_name):
        """The native format, and hopefully most reliable,
        stable, and generally best way of saving, loading,
        or creating Hypatia scenes.

        This defines the standard by which all
        other Scene constructors must follow.

        Args:
          scene_name (str): the name of the directory which corresponds
            to the map you want to load from resources/maps.

        """

        # load the scene zip from the scene resource and read
        # the general scene configuration, first.
        resource = resources.Resource('scenes', scene_name)
        scene_ini = resource['scene.ini']

        # Construct a TileMap from the tilemap.txt
        # contents from the scene resource.
        tilemap_string = resource['tilemap.txt']
        tilemap = tiles.TileMap.from_string(tilemap_string)

        # Get the player's starting position from the
        # general scene configuration.
        player_start_x = scene_ini.getint('general', 'player_start_x')
        player_start_y = scene_ini.getint('general', 'player_start_y')
        player_start_position = (player_start_x, player_start_y)

        # Create a player using the player
        # start position found.
        human_player = self.create_human_player(player_start_position)

        # npcs.ini
        #
        # Create a list of NPCs using a configuration file
        # from the scene resource.
        npcs_ini = resource['npcs.ini']

        npcs = []

        # each section title is the npc's name,
        # each sections key/value pairs are
        # the NPC's attributes.
        for npc_name in npcs_ini.sections():

            if npcs_ini.has_option(npc_name, 'walkabout'):
                # The NPC's walkabout resource name
                walkabout_name = npcs_ini.get(npc_name, 'walkabout')

            # the required (x, y) pixel coordinates referring
            # to the position of this NPC
            position_x = npcs_ini.getint(npc_name, 'position_x')
            position_y = npcs_ini.getint(npc_name, 'position_y')
            position = (position_x, position_y)

            # create the NPC's walkabout using the
            # designated walkabout name and position
            # from the NPC's config.
            npc_walkabout = sprites.Walkabout(walkabout_name,
                                              position=position)

            if npcs_ini.has_option(npc_name, 'say'):
                # Load some say text for the NPC, so when
                # an actor uses talk() on them, they say
                # this message--the say_text!
                say_text = npcs_ini.get(npc_name, 'say')
            else:
                say_text = None

            npc = player.Npc(walkabout=npc_walkabout, say_text=say_text)
            npcs.append(npc)

        return Scene(
                     tilemap=tilemap,
                     player_start_position=player_start_position,
                     human_player=human_player,
                     npcs=npcs
                    )

    def collide_check(self, rect):
        """Returns True if there are collisions with rect.

        Args:
            rect (pygame.Rect): The area/rectangle which
                to test for collisions against NPCs and
                the tilemap's wallmap.

        Notes:
            Should use pygame.sprite.spritecollide()

        """

        possible_collisions = self.tilemap.impassable_rects

        for npc in self.npcs:
            possible_collisions.append(npc.walkabout.rect)

        return rect.collidelist(possible_collisions) != -1

    def runtime_setup(self):
        """Initialize all the NPCs, tilemap, etc.

        Is this a horrible way of doing this? I dunno,
        not the fondest...

        """

        npcs_to_setup = tuple(npc.walkabout for npc in self.npcs)
        objects_to_setup = (self.tilemap, self.human_player.walkabout,)
        objects_to_setup = objects_to_setup + npcs_to_setup

        for object_to_setup in objects_to_setup + npcs_to_setup:
            object_to_setup.runtime_setup()

    def render(self, viewport, clock):
        """Render this Scene onto viewport.

        Args:
            viewport (render.Viewport): The global/master viewport,
                where stuff will be blitted to. Also used for some
                calculations.
            clock (pygame.time.Clock): Global/master/the game
                clock used for timing in this game.

        """

        (self.tilemap.tilesheet.animated_tiles_group.
         update(clock, viewport.surface, viewport.rect.topleft))
        first_tilemap_layer = self.tilemap.layer_images[0]
        viewport.center_on(self.human_player.walkabout,
                           first_tilemap_layer.get_rect())
        viewport.blit(first_tilemap_layer)
        self.tilemap.blit_layer_animated_tiles(viewport, 0)

        # render each npc walkabout
        # should use group draw
        for npc in self.npcs:
            npc.walkabout.blit(
                               clock,
                               viewport.surface,
                               viewport.rect.topleft
                              )

        # finally human and rest map layers last
        self.human_player.walkabout.blit(
                                         clock,
                                         viewport.surface,
                                         viewport.rect.topleft
                                        )

        for i, layer in enumerate(self.tilemap.layer_images[1:], 1):
            viewport.blit(layer)
            self.tilemap.blit_layer_animated_tiles(viewport, i)


class TMX(object):
    """`TMX` object to represent and "translate"
    supported Scene data from a TMX file.

    TMX files are capable of providing the information
    required to instantiate TileMap and Scene.

    TMX file must have the following settings:

      * orientation: orthogonal
      * tile layer format: csv
      * tile render order: right down

    You must also specify the tilesheet name you want to use
    in Hypatia, as your tileset image name. You may only use
    one image.

    Constants:
        SUPPORTED (str): the TMX file format which is supported.

    Attributes:
        root (ElementTree): the XML ElementTree root of the TMX file.
        player_start_position (tuple): (x, y) coordinate in which
            the player begins this scene at.
        layers (list): a 3D list of tile IDs referring to a tile
            by id in a Tilesheet. This data is extrapolated from
            a CSV-format list of tile IDs.
        npcs (List[players.Npc]): --

    See Also:
        http://doc.mapeditor.org/reference/tmx-map-format/

    """

    SUPPORTED = '1.0'

    def __init__(self, path_or_readable):
        """Read XML from path_or_readable, validate the TMX as being
        supported by Hypatia, and set all supported information as
        attributes.

        Args:
            path_or_readable (str|file-like-object): This is
                plopped right into ElementTree.parse().

        Note:
            This method is under-documented!

        """

        # parse TMXML for TileMap-specific/supported data
        tree = ET.parse(path_or_readable)
        self.root = tree.getroot()  # <map ...>

        # check the version first, make sure it's supported
        map_version = self.root.attrib['version']

        if map_version != self.SUPPORTED:

            raise exceptions.TMXVersionUnsupported(map_version)

        # Get the Tilesheet (tileset) name from the tileset
        tileset_images = self.root.findall('.//tileset/image')

        if len(tileset_images) > 1:

            # too many tilesets!
            raise exceptions.TMXTooManyTilesheets()

        tileset = self.root.find('.//tileset')
        tilesheet_name = tileset.attrib['name']

        # get the 3D constructor/blueprint of TileMap,
        # which simply references, by integer, the
        # tile from tilesheet.
        layers = []

        for layer_data in self.root.findall(".//layer/data"):
            data_encoding = layer_data.attrib['encoding']

            if data_encoding != 'csv':

                raise exceptions.TMXLayersNotCSV(data_encoding)

            layer_csv = layer_data.text.strip()
            rows = layer_csv.split('\n')
            parsed_rows = []

            for row in rows:
                # TMX tilesets start their ids at 1, Hypatia Tilesheets
                # starts ids at 0.
                cells = row.split(',')[:-1]  # trailing comma
                parsed_row = [int(tile_id) - 1 for tile_id in cells]
                parsed_rows.append(parsed_row)

            layers.append(parsed_rows)

        self.tilemap = tiles.TileMap(tilesheet_name, layers)

        # loop through objects in the object layer to find the player's
        # start position and NPC information.
        self.npcs = []
        self.player_start_position = None

        for tmx_object in self.root.findall(".//objectgroup/object"):
            object_type = tmx_object.attrib['type']
            x = int(tmx_object.attrib['x'])
            y = int(tmx_object.attrib['y'])

            if object_type == 'player_start_position':
                self.player_start_position = (x, y)
            elif object_type == 'npc':
                properties = tmx_object.find('properties')
                xpath = ".//property[@name='%s']"

                position = (x, y)
                walkabout_name = (properties.find(xpath % 'walkabout').
                                  attrib['value'])
                walkabout = sprites.Walkabout(walkabout_name, position)
                say_text = properties.find(xpath % 'say').attrib['value']

                npc = player.Npc(walkabout=walkabout, say_text=say_text)
                self.npcs.append(npc)

        # should use xpath before loading all npcs...
        if self.player_start_position is None:

            raise exceptions.TMXMissingPlayerStartPosition()
