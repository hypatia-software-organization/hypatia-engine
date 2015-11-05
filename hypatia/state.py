import pygame
import traceback

from pygame.locals import *

from hypatia import util


class State(object):
    def __init__(self, parent):
        """Defines a game state. This could be a menu, the game interaction
        itself, or something else.

        Arguments:
            parent (Game): The game that this State belongs to
        """

        self.parent = parent
        self.surface = pygame.Surface(parent.screen_size)

    def startup(self):
        """Perform state startup.
        """

        pass

    def shutdown(self):
        """Perform state shutdown. Called before the state is removed.
        """

        pass

    def suspend(self):
        """Suspend the state. Called before a new state is added to the stack.
        """

        pass

    def resume(self):
        """Resume the state. Called upon a state pop causing this state to
        become the active state.
        """

        pass

    def update(self):
        """Update the state's surface.
        """

        pass

    def handle_event(self, event):
        """Handle a single pygame event for this state.

        Arguments:
            event (pygame.Event): The event to handle
        """

        pass

class ExceptionDisplayState(State):
    """This state displays exceptions that may arise during the game.

    It is automatically called if an unhandled exception arises in the game.
    """

    def startup(self):
        self.renderables = []

        fontstack = "dejavusans,sans"
        font = pygame.font.SysFont(fontstack, 16)
        frender = lambda f, t: f.render(t, True, (255, 255, 255))

        ypos = 8 # initial padding on the top
        
        # get the exception stacktrace and print it to the console
        excinfo = traceback.format_exc()
        print(excinfo)

        # width of our display surface
        surfacewidth = self.parent.screen_size[0] - 16

        # wrap lines of the stacktrace, add them all to exclines
        exclines = []
        exclineheight = 0 # this gets set to the maximum line-height

        for i in excinfo.splitlines():
            for line in util.wrapline(i, font, surfacewidth):
                exclines.append(frender(font, i))
                exclineheight = max(exclineheight, font.size(line)[1])

        # calculate the size of the surface we need to create
        excsurfacesize = (
            surfacewidth,
            len(exclines) * (exclineheight + 8) # the + 8 is line padding
            )

        # actually create the surface and blit the lines to it
        self.excsurface = pygame.Surface(excsurfacesize)
        self.excsurface.fill((51, 51, 51))
        
        for i, l in enumerate(exclines):
            self.excsurface.blit(l, (0, i * (exclineheight + 8)))

        # create a surface based on the screen size in which we render the
        # other exception surface. this allows scrolling without the text
        # rendering underneath other things that are being displayed (like
        # the buttons)

        displaysurfacesize = (
            self.parent.screen_size[0] - 16,
            self.parent.screen_size[1] - 16 - 48 # allow for buttons
        )

        self.displaysurface = pygame.Surface(displaysurfacesize)

        # dstore how far down we've scrolled (0 being the top)
        self.scrollpos = 0

    def handle_event(self, event):
        """Handle keypresses and scrolling for the exception display.
        """

        viewportrect = self.displaysurface.get_rect().move(8, 8)

        if event.type == KEYDOWN:
            if event.key == K_PAGEDOWN:
                self.scrollpos -= 100
            elif event.key == K_PAGEUP:
                self.scrollpos += 100

        """
        elif event.type == MOUSEBUTTONDOWN:    
            if viewportrect.collidepoint(event.pos):
                # event.button: 4 is scrollup, 5 is scrolldown
                pass
        """

        # sanity checks to make sure we haven't scrolled off-screen

        maxdownscroll = (self.excsurface.get_rect().height - 
            self.displaysurface.get_rect().height)

        if self.scrollpos < -maxdownscroll:
            self.scrollpos = -maxdownscroll

        if self.scrollpos > 0:
            self.scrollpos = 0


    def update(self):
        super(ExceptionDisplayState, self).update()
        
        self.displaysurface.fill((51, 51, 51))
        self.displaysurface.blit(self.excsurface, (0, self.scrollpos))
        self.surface.blit(self.displaysurface, (8, 8))
