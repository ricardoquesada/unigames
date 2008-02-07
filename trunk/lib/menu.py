#
# Menu class for pyglet
# $Id$
#

from pyglet import font
from scene import Scene, Layer
from director import *

from pyglet import media
from pyglet import window

class Menu(Scene):


    def __init__( self, *args, **kwargs ):
        super(Menu, self).__init__(*args, **kwargs)

        self.title = kwargs['title']
        self.options = kwargs['options']

        self.font_title= 'KonQa Black'
        self.font_title_size = 72
        self.font_options = 'You Are Loved'
        self.font_options_size = 48
        self.font_options_selected_size = 64 

        self.selected_option = 0

        title_layer= self.new_layer("title")
        options_layer = self.new_layer("options")

        font.add_directory('data')
        ft = font.load( self.font_title, self.font_title_size )
        ft_height = ft.ascent - ft.descent
        text = font.Text(ft, self.title)

        fo = font.load( self.font_options, self.font_options_size )
        fo_selected = font.load( self.font_options, self.font_options_selected_size )
        fo_height = int ( (fo.ascent - fo.descent) * 0.9 )

        win = Director()

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
            text.color = ( 0.8, 0.8, 0.8, 1.0 )
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
            self.sound = media.load('data/menuchange.wav', streaming=False)

    def dispatch_events( self ):
        pass

    def enter( self ):
        Director().push_handlers( self.on_key_press )

    def leave( self ):
        Director().pop_handlers()

    def on_key_press( self, symbol, modifier ):
        if symbol == window.key.DOWN or symbol == window.key.UP:
            layer = self.get_layer('options')
            layer.get_item( self.selected_option * 2 ).visible = True
            layer.get_item( self.selected_option * 2 + 1 ).visible = False

            if symbol == window.key.DOWN:
                self.selected_option += 1

            elif symbol == window.key.UP:
                self.selected_option -= 1

            if self.selected_option < 0:
                self.selected_option = len( self.options ) -1
            elif self.selected_option > len( self.options ) - 1:
                self.selected_option = 0

            layer.get_item( self.selected_option *2 ).visible = False
            layer.get_item( self.selected_option *2 + 1 ).visible = True

            self.sound.play()

        elif symbol == window.key.ENTER:
            print self.selected_option
            
