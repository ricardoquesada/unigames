# $Id$
# heavyly based on code from: "Typos Pocus" http://www.pyweek.org/e/PyAr2/

import hollow
import pygame
from pygame.locals import *
from euclid import *

class Menu:
    def __init__(self, font, font_selected, opts, margin=0, normal_color=(255,255,255), selected_color=(255,255,255), selected_border_color=None, normal_border_color=None,rectangle=Point2(0,0)):
        self.font = font
        self.font_selected = font_selected
        if selected_border_color == None:
            selected_border_color = (0,0,0)
        if normal_border_color == None:
            normal_border_color = (0,0,0)
        self.margin = margin
        self.opts = opts
        self.selected = 0
        self.selected_img = []
        self.unselected_img = []
        self.rectangle=rectangle
        
        line_step = 0
        for tuple in self.opts:
            text = tuple[0]
            sel = hollow.textOutline(font_selected, text, selected_color, selected_border_color )
            unsel = hollow.textOutline(font, text, normal_color, normal_border_color )
            self.selected_img.append( sel )
            self.unselected_img.append( unsel )
            line_step = max(max(sel.get_height(), unsel.get_height())+self.margin, line_step)
            
        self.line_step = line_step
            
                
    def blit(self, surface ):
        for i in range(len(self.opts)):
            
            if i == self.selected:
                img = self.selected_img[i]
            else:
                img = self.unselected_img[i]
                
            x = self.rectangle.x - img.get_width()/2
            y = self.rectangle.y + self.line_step * i - img.get_height()/2
            
            surface.blit( img, (x,y) )
            
    def next(self):
        self.selected = (self.selected + 1)%len(self.opts)
        
    def prev(self):
        self.selected = (self.selected - 1)%len(self.opts)     
        
    def set_mouse(self, x, y):
        i = self.get_mouse_over(x,y)
        if i is not None and  i != self.selected:
            self.selected = i
            return True        
    
    def get_mouse_over(self, x, y):
        for i in range(len(self.opts)):
            img = self.selected_img[i]
                
            tx = 0-img.get_width()/2
            ty = 0 + self.line_step * i - img.get_height()/2
            
            if tx <= x <= tx+img.get_width():
                if ty+10 <= y <= ty+img.get_height()-10:
                    return i
        return None
        
    def click_mouse(self, x, y):
        i = self.get_mouse_over(x,y)
        if i is not None:
            return i      

    def update_event(self, evt):
        """Handles keyboard or mouse events. Return True if background needs to be re-painted"""
        if evt.type == MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            x -= self.rectangle.x
            y -= self.rectangle.y
            if self.set_mouse(x,y):
                return True
        elif evt.type == MOUSEBUTTONUP:
            x, y = pygame.mouse.get_pos()
            x -= self.rectangle.x
            y -= self.rectangle.y
            sel = self.click_mouse(x,y)
            if sel is not None:
                self.opts[sel][1]()
        elif evt.type == KEYDOWN:
            if evt.key == K_ESCAPE:
                self.end()
            elif evt.key == K_DOWN:
                self.next()
                return True
            elif evt.key == K_UP:
                self.prev()
                return True
            elif evt.key in [K_RETURN, K_SPACE]:
                self.opts[self.selected][1]()
        return False
