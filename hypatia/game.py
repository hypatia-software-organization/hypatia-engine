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
import tempfile
import datetime

try:
    import ConfigParser as configparser

except ImportError:
    import configparser

import pygame
from pygame.locals import *

from hypatia import util
from hypatia import scene
from hypatia import render
from hypatia import constants

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
        self.config.readfp(self.vfs.open("/game/game.ini"))

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

class GameStage(Stage):
    """The stage that handles displaying tilemaps and dealing with user
    interaction.
    """

    def __init__(self, parent, scene):
        super(GameStage, self).__init__(parent)
        self.scene = scene

    def startup(self):
        # Assume that the scene we were given has the tilemap and everything
        # already loaded, so just do runtime setup and display stuff in here

        pass

class ExceptionStage(Stage):
    def startup(self):
        self.renderables = []

        fontstack = "dejavusans,sans"
        font = pygame.font.SysFont(fontstack, 22)
        frender = lambda f, t: f.render(t, True, (255, 255, 255))

        ypos = 8

        # the exception info goes here
        exctype, excval = sys.exc_info()[:2]
        text = exctype.__name__
        if 'message' in dir(excval):
            text = "%s: %s" % (exctype.__name__, excval.message)

        lines = util.wrapline(text, font, self.parent.screen_size[0] - 16)
        for line in lines:
            t = frender(font, line)
            self.renderables.append((t, (8, ypos)))
            ypos += t.get_rect().height + 8

        # format the full traceback and put that into a surface that we can
        # scroll through on the exception info. maybe use Viewport?
        excinfo = traceback.format_exc()
        print(excinfo)

        excsurface = pygame.Surface((self.parent.screen_size[0] - 16, 1000))
        excypos = 0
        for i in excinfo.splitlines()[:-1]:
            t = frender(font, i)
            excsurface.blit(t, (0, excypos))
            excypos += t.get_rect().height + 4

        # save on dat memory by clipping down the generated surface
        newsize = (self.parent.screen_size[0] - 16, excypos)
        self.excsurface = pygame.Surface(newsize)
        self.excsurface.blit(excsurface, (0, 0))
        del excsurface 

        viewportsize = (self.parent.screen_size[0] - 16,
                        self.parent.screen_size[1] - ypos - 64)

        self.excviewport = render.Viewport(viewportsize)
        self.excviewportpos = (8, ypos)

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            viewportrect = self.excviewport.rect.move(self.excviewportpos)
            if viewportrect.collidepoint(event.pos):
                # event.button: 4 is scrollup, 5 is scrolldown

                if event.button == 4 and self.excviewport.rect.y > 0:
                    self.excviewport.rect.move_ip(0, -10)

                if event.button == 5:
                    height = self.excviewport.rect.y + self.excviewport.rect.height
                    if height < self.excsurface.get_rect().height:
                        self.excviewport.rect.move_ip(0, 10)

    def update(self):
        super(ExceptionStage, self).update()
        self.surface.fill((51, 51, 51))

        for i in self.renderables:
            self.surface.blit(*i)

        self.excviewport.blit(self.excsurface)
        self.surface.blit(self.excviewport.surface, self.excviewportpos)
