__docformat__ = 'restructuredtext'
__version__ = '$Id$'

from menu import Menu
import director

class GameMenu(Menu):
    def __init__( self ):
        super( GameMenu, self ).__init__( self, title="UNIGAMES", options=("New Game", "Scores", "Options", "Full Screen", "Quit" ) )


def run():
    d = director.Director( caption = "Unigames" )
    d.run( GameMenu() )

if __name__ == "__main__":
    run()
