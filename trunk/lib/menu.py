#
# Menu class for pyglet
# $Id$
#

from pyglet import font
from scene import Scene, Layer
from director import *

from pyglet import media
from pyglet import window

__all__ = [ 'Menu' ]

class Menu(Scene):


    def __init__( self, *args, **kwargs ):
        super(Menu, self).__init__(*args, **kwargs)

        #
        # Menu default options
        #
        self.font_title= 'KonQa Black'
        self.font_title_size = 72
        self.font_options = 'You Are Loved'
        self.font_options_size = 48
        self.font_options_selected_size = 64 

        self.sound = media.load('data/menuchange.wav', streaming=False)

        self.selected_option = 0

        self.title = kwargs['title']
        self.options = [ item[0] for item in kwargs['options'] ]    #  map( lambda x: x[0], kwargs['options'] )
        self.options_cb = [ item[1] for item in kwargs['options'] ]    #  map( lambda x: x[1], kwargs['options'] )

        self.init_menu()

        title_layer= self.new_layer("title")
        options_layer = self.new_layer("options")

        font.add_directory('data')
        ft = font.load( self.font_title, self.font_title_size )
        ft_height = ft.ascent - ft.descent
        text = font.Text(ft, self.title)

        fo = font.load( self.font_options, self.font_options_size )
        fo_selected = font.load( self.font_options, self.font_options_selected_size )
        fo_height = int ( (fo.ascent - fo.descent) * 0.9 )

        win = director.get_window()

        text = font.Text(ft, self.title,
            x=win.width / 2,
            y=win.height - 40,
            halign=font.Text.CENTER,
            valign=font.Text.CENTER)
        text.visible = True
        text.color = ( 1.0, 1.0, 1.0, 0.2 )

        title_layer.append( text )

        for idx,opt in enumerate( self.options ):

            # Unselected option
            text = font.Text( fo, opt,
                x=win.width / 2,
                y=win.height / 2 + (fo_height * len(self.options) )/2 - (idx * fo_height ) ,
                halign=font.Text.CENTER,
                valign=font.Text.CENTER)
            text.visible = (idx != self.selected_option )
            text.color = ( 0.6, 0.6, 0.6, 1.0 )
            options_layer.append( text )

            # Selected Option
            text = font.Text( fo_selected, opt,
                x=win.width / 2,
                y=win.height / 2 + (fo_height * len(self.options) )/2 - (idx * fo_height ) ,
                halign=font.Text.CENTER,
                valign=font.Text.CENTER)
            text.visible = ( idx == self.selected_option )
            text.color = ( 1.0, 1.0, 1.0, 1.0 )
            options_layer.append( text )

            # 

    #
    # Should be overrided in subclass to specify a custom fonts, 
    # font size, etc.
    #
    def init_menu( self ):
        pass

    #
    # Called once per tick
    #
    def dispatch_events( self ):
        pass

    #
    # Called when the menu will appear
    #
    def enter( self ):
        director.push_handlers( self.on_key_press )

    #
    # Called when the menu will disappear
    #
    def exit( self ):
        director.pop_handlers()

    #
    # Called everytime a key is pressed
    #
    def on_key_press( self, symbol, modifier ):
        if symbol == window.key.DOWN or symbol == window.key.UP:
            layer = self.get_layer('options')
            layer[ self.selected_option * 2 ].visible = True
            layer[ self.selected_option * 2 + 1 ].visible = False

            if symbol == window.key.DOWN:
                self.selected_option += 1

            elif symbol == window.key.UP:
                self.selected_option -= 1

            if self.selected_option < 0:
                self.selected_option = len( self.options ) -1
            elif self.selected_option > len( self.options ) - 1:
                self.selected_option = 0

            layer[ self.selected_option *2 ].visible = False
            layer[ self.selected_option *2 + 1 ].visible = True

            self.sound.play()

        elif symbol == window.key.ENTER:
            print self.selected_option
            self.options_cb[ self.selected_option]()


class MenuItem( object ):

    def __init__(self, label, activate_func):
        self.y = 0
        self.label = lael
        self.activate_func = activate_func

    def draw(self, selected):
        self.text.draw()


    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER and self.activate_func:
            self.activate_func()
            if enable_sound:
                bullet_sound.play()
