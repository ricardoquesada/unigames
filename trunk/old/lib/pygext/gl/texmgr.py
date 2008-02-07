"""Texture binding optimization"""

__all__ = [
    "bind_texture",
    ]

from OpenGL.GL import glBindTexture, GL_TEXTURE_2D

_curtex = None

def bind_texture(texid):
    global _curtex
    if texid == _curtex:
        return
    glBindTexture(GL_TEXTURE_2D, texid)
    _curtex = texid
