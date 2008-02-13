#
#
# Menu class for pyglet
# riq - 2008
#
# Ideas borrowed from:
#    pygext: http://opioid-interactive.com/~shang/projects/pygext/
#    pyglet astraea: http://www.pyglet.org
#    Grossini's Hell: http://www.pyweek.org/e/Pywiii/ 
# 
#

from pyglet import font
from scene import Scene
from director import *

from pyglet import media
from pyglet import window
from pyglet.window import key
from pyglet.gl import *

__all__ = [ 'Menu', 'MenuItem', 'ToggleMenuItem' ]

#
# Class Menu
#

# Horizontal Align
CENTER = font.Text.CENTER
LEFT = font.Text.LEFT
RIGHT = font.Text.RIGHT

# Vertial Align
TOP = font.Text.TOP
BOTTOM = font.Text.BOTTOM



class Menu(Scene):

    def __init__( self, title = ''):
        super(Menu, self).__init__()

        #
        # Items and Title
        #
        self.items = []
        self.title = title
        self.title_text = None

        #
        # Menu default options
        # Menus can be customized changing these variables
        #

        # Title
        self.font_title = ''            # Full font name
        self.font_title_size = 48

        # Items
        self.font_items = ''            # Full font name
        self.font_items_size = 48
        self.font_items_selected_size = 64 

        # Sound
        self.sound = media.load('data/menuchange.wav', streaming=False)

        # Alignment
        self.menu_halign = CENTER
        self.menu_valign = CENTER
     
    def draw_title( self ):
        """ draws the title """
        win = director.get_window()
        ft = font.load( self.font_title, self.font_title_size )
        ft_height = ft.ascent - ft.descent
        text = font.Text(ft, self.title)

        text = font.Text(ft, self.title,
            x=win.width / 2,
            y=win.height - 40,
            halign=font.Text.CENTER,
            valign=font.Text.CENTER)
        text.color = ( 0.6, 0.6, 0.6, 1.0 )

        self.title_text = text

    def draw_items( self ):
        win = director.get_window()
        fo = font.load( self.font_items, self.font_items_size )
        fo_selected = font.load( self.font_items, self.font_items_selected_size )
        fo_height = int( (fo.ascent - fo.descent) * 0.9 )

        if self.menu_halign == CENTER:
            pos_x = win.width / 2
        elif self.menu_halign == RIGHT:
            pos_x = win.width - 2
        elif self.menu_halign == LEFT:
            pos_x = 2
        else:
            raise Exception("Invalid halign value for menu")

        for idx,item in enumerate( self.items ):

            # Unselected option
            item.text = font.Text( fo, item.label,
                x=pos_x,
                y=win.height / 2 + (fo_height * len(self.items) )/2 - (idx * fo_height ) ,
                halign=self.menu_halign,
                valign=font.Text.CENTER)
            item.text.color = ( 0.6, 0.6, 0.6, 1.0 )

            # Selected option
            item.text_selected = font.Text( fo_selected, item.label,
                x=pos_x,
                y=win.height / 2 + (fo_height * len(self.items) )/2 - (idx * fo_height ) ,
                halign=self.menu_halign,
                valign=font.Text.CENTER)
            item.text_selected.color = ( 1.0, 1.0, 1.0, 1.0 )

    def add_item( self, item ):
        self.items.append( item )

    # overriden method from Scene
    def draw( self ):
        self.title_text.draw()
        for i in self.items:
            i.draw()

    def tick( self, dt ):
        for i in self.items:
            i.tick( dt )

    def reset( self ):
        self.draw_title()
        self.draw_items()
        self.selected_index = 0
        self.items[ self.selected_index ].selected = True

    #
    # Should be overrided in subclass to specify a custom fonts, 
    # font size, etc.
    #
    def init_menu( self ):
        pass

    #
    # Called when the menu will appear
    #
    def enter( self ):
#        director.get_window().push_handlers( self.on_key_press, self.on_mouse_motion )
        director.get_window().push_handlers( self.on_key_press )

    #
    # Called when the menu will disappear
    #
    def exit( self ):
        director.get_window().pop_handlers()

    #
    # Called everytime a key is pressed
    # return True to avoid passing the event to another handler
    #
    def on_key_press(self, symbol, modifiers):

        old_idx = self.selected_index

        if symbol == key.DOWN:
            self.selected_index += 1
        elif symbol == key.UP:
            self.selected_index -= 1
        elif symbol == key.ESCAPE:
            self.on_quit()
            return True
        else:
            ret = self.items[self.selected_index].on_key_press(symbol, modifiers)

        if self.selected_index< 0:
            self.selected_index= len( self.items ) -1
        elif self.selected_index > len( self.items ) - 1:
            self.selected_index = 0

        if symbol in (key.DOWN, key.UP):
            self.items[ old_idx ].selected = False
            self.items[ self.selected_index ].selected = True 
            self.sound.play()
            return True

        return ret

    def on_mouse_motion( self, x, y, dx, dy ):
        pass
            

    #
    # Called everytime you press escape
    #
    def on_quit( self ):
        pass        # override in subclases


#
# MenuItem
#
class MenuItem( object ):

    def __init__(self, label, activate_func):
        self.label = label
        self.activate_func = activate_func

        self.selected = False

        self.text = None
        self.text_selected = None

    def draw( self ):
        if self.selected:
            self.text_selected.draw()
        else:
            self.text.draw()

    def tick( self, dt ):
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER and self.activate_func:
            self.activate_func()
            return True

#
# Item that can be toggled
#
class ToggleMenuItem( MenuItem ):

    def __init__(self, label, value, toggle_func):
        self.toggle_label = label
        self.value = value
        self.toggle_func = toggle_func
        super(ToggleMenuItem, self).__init__( self.get_label(), None )

    def get_label(self):
        return self.toggle_label + (self.value and ': ON' or ': OFF')

    def tick( self, dt ):
        # useful to animate the items
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol in ( key.LEFT, key.RIGHT, key.ENTER):
            self.value = not self.value
            self.text.text = self.get_label()
            self.text_selected.text = self.get_label()
            self.toggle_func( self.value )
            return True
