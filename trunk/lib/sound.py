import pygame


def init_music():
    pygame.mixer.pre_init(44100, -16, False, 1024)
    pygame.mixer.init()
    pygame.mixer.set_reserved(1)

def play_song( filename ):
    pygame.mixer.music.load( "data/music/%s.ogg" % filename  )
    pygame.mixer.music.play()
