
import math
import pygame
from pygame.locals import *
from OpenGL.GL import *

import pygext.gl as gl
from pygext.gl.vector.primitives import *
from pygext.gl.shapes import draw_shape, Bitmap

class EditorObject(object):
    def __init__(self, shape, x ,y):
        self.shape = shape
        self.x = x
        self.y = y

def loadimg(path, img):
    import os
    i = pygame.image.load(os.path.join(path,img))
    return Bitmap(i)

class ToolbarItem(object):
    def __init__(self, name, img, callback):
        self.name = name
        self.img = img
        self.callback = callback

class Toolbar(object):
    def __init__(self):
        self.items = []
        self.selected = None

    def draw(self):
        glBegin(GL_QUADS)
        glColor3f(0,0,0)
        glVertex2f(0,0)
        glVertex2f(50,0)
        glVertex2f(50,600)
        glVertex2f(0,600)
        glColor3f(0.4,0.4,0.4)
        glVertex2f(5,5)
        glVertex2f(45,5)
        glVertex2f(45,595)
        glVertex2f(5,595)
        glEnd()
        y = 10
        for item in self.items:
            if item is self.selected:
                r = rect(4,y-4,40,40).fillcolor(255,255,255)
                draw_shape(r, 0, 0)
            draw_shape(item.img, 8, y)
            y += 40


    def add(self, action, icon, callback):
        import imp, os
        path = imp.find_module("pygext")[1]
        gfxpath = os.path.join(path, "gl", "vector", "editor", "gfx")
        self.items.append(ToolbarItem(action, loadimg(gfxpath, icon),callback))

    def item(self, y):
        if y < 10: return None
        i = (y-10)/40
        if i >= len(self.items):
            return None
        return self.items[i]

class Editor(object):

    def __init__(self):
        gl.init((800,600),(800,600))
        glClearColor(0.15,0.15,0.15,1)
        self.state = None
        self.quit = False
        pygame.mouse.set_visible(0)
        self.shapes = []
        self.fillcolor = (200,200,200)
        self.linecolor = None
        self.toolbar = Toolbar()
        self.init_toolbar()
        self.set_state(MainState)

    def init_toolbar(self):
        t = self.toolbar
        t.add("rect", "button_rect1.png", lambda: self.set_state(CreateState,"rect"))
        t.add("circle", "button_circle1.png", lambda: self.set_state(CreateState,"circle"))
        t.add("poly", "button_poly1.png", lambda: self.set_state(CreateState,"poly"))

    def draw_cursor(self):
        mx,my = pygame.mouse.get_pos()
        glLineWidth(2)
        glBegin(GL_LINES)
        glColor4f(0,0,0,0.5)
        glVertex2f(mx,my-10)
        glVertex2f(mx,my+10)
        glVertex2f(mx-10,my)
        glVertex2f(mx+10,my)
        mx += 1
        my += 1
        glColor4f(1,1,1,0.5)
        glVertex2f(mx,my-10)
        glVertex2f(mx,my+10)
        glVertex2f(mx-10,my)
        glVertex2f(mx+10,my)
        glEnd()

    def draw_grid(self):
        glLineWidth(1)
        glDisable(GL_LINE_SMOOTH)
        glBegin(GL_LINES)
        glColor3f(0.4,0.4,0.4)
        glVertex2f(450,0)
        glVertex2f(450,600)
        glVertex2f(0,300)
        glVertex2f(800,300)
        glEnd()


    def draw_toolbar(self):
        self.toolbar.draw()

    def handle_toolbar(self, x, y):
        item = self.toolbar.item(y)
        if item is None:
            self.toolbar.selected = None
            return
        item.callback()
        self.toolbar.selected = item

    def mainloop(self):
        pygame.event.set_allowed(None)
        pygame.event.set_allowed([KEYDOWN,QUIT,MOUSEBUTTONDOWN,MOUSEMOTION,MOUSEBUTTONUP])

        clock = pygame.time.Clock()
        while not self.quit:
            gl.clear_screen()
            
            self.draw_grid()
            self.draw_toolbar()

            for obj in self.shapes:
                draw_shape(obj.shape, obj.x, obj.y)

            self.draw_cursor()

            events = pygame.event.get()
            for ev in events:
                if ev.type == QUIT:
                    self.quit = True
                elif ev.type == KEYDOWN:
                    self.state.handle_key(ev)
                elif ev.type == MOUSEBUTTONDOWN:
                    mx,my = pygame.mouse.get_pos()
                    if mx <= 50:
                        self.handle_toolbar(mx,my)
                    else:
                        self.state.handle_click(ev)
                elif pygame.mouse.get_pressed()[0] and ev.type == MOUSEMOTION:
                    self.state.handle_drag(ev)
                elif ev.type == MOUSEBUTTONUP:
                    self.state.handle_dragend(ev)
            self.state.render()
            gl.flip_screen()
            clock.tick(50)

    def set_state(self, cls, *args):
        if self.state is not None:
            self.state.exit()
        self.state = cls(self)
        self.state.enter(*args)
        self.toolbar.selected = None

class State(object):
    def __init__(self, editor):
        self.editor = editor

    def change(self, new_state, *args):
        self.editor.set_state(new_state, *args)

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_key(self, ev):
        pass

    def handle_click(self, ev):
        pass

    def handle_drag(self, ev):
        pass

    def handle_dragend(self, ev):
        pass

    def render(self):
        pass

class MainState(State):
    def enter(self):
        print
        print "Commands:"
        print "e - edit"
        print "s - save"
        print "l - load"
        print "q - quit"

        self.selected = None
        self.drag = None

    def handle_toolbar(self):
        x,y = pygame.mouse.get_pos()
        if not (8 <= x <= 42):
            return
        if 10 <= y <= 42:
            self.change(CreateState, "rect")
        elif 50 <= y <= 82:
            self.change(CreateState, "circle")
        elif 90 <= y <= 122:
            self.change(CreateState, "poly")            

    def handle_key(self, ev):
        if ev.key == K_q:
            self.editor.quit = True
        if ev.key == K_e:
            self.change(EditState, self.selected)
        if ev.key == K_DELETE:
            if self.selected is not None:
                self.editor.shapes.remove(self.selected)
                self.selected = None

    def handle_click(self, ev):
        mx,my = pygame.mouse.get_pos()
        if mx < 50:
            self.handle_toolbar()
            return
        self.selected = None
        if ev.button == 3:
            self.drag = None
            return
        shapes = self.editor.shapes[:]
        shapes.reverse()
        for obj in shapes:
            p = obj.shape.transformed_polygon()
            p.shift(obj.x,obj.y)
            if p.isInside(mx,my):
                self.selected = obj
                return

    def handle_drag(self, ev):
        if not self.selected:
            self.drag = None
            return
        x,y = ev.rel
        if x == 0 and y == 0:
            return
        if self.drag is not None:
            x += self.drag[0]
            y += self.drag[1]
        self.drag = (x,y)

    def handle_dragend(self, ev):
        if not self.drag:
            return
        if not self.selected:
            self.drag = None
            return
        dx,dy = self.drag
        self.selected.x += dx
        self.selected.y += dy
        self.drag = None

    def render(self):
        obj = self.selected
        if obj is None:
            return
        x,xx,y,yy = obj.shape._polygon.boundingBox()
        cx = obj.x
        cy = obj.y
        if self.drag is not None:
            dx,dy = self.drag
            cx += dx
            cy += dy
        glBegin(GL_LINES)
        #glDisable(GL_LINE_SMOOTH)
        glColor4f(1,1,1,0.7)
        glVertex2f(cx,cy-5)
        glVertex2f(cx,cy+5)
        glVertex2f(cx-5,cy)
        glVertex2f(cx+5,cy)
        glEnd()
        box = rect(cx+x-2,cy+y-2,xx-x+4,yy-y+4).linecolor(255,255,255,150).linewidth(2)
        draw_shape(box, 0, 0)
        if self.drag is not None:
            ghost = poly(obj.shape).linecolor(255,255,255,150)
            draw_shape(ghost, cx, cy)

def _angle(x,y, xx,yy):
    A = N.array([x,y])
    B = N.array([xx,yy])
    B = B-A
    A = [0,-1]
    B = B / math.sqrt(xx*xx+yy*yy)
    dot = N.dot(A,B)
    return math.acos(dot) / math.pi * 180.0

class EditState(MainState):
    def enter(self, selected):
        print "\nEdit:"
        print "f - fill color"
        print "l - line color"
        print "s - scale"
        print "r - rotate"
        print "x - skewx"
        print "y - skewy"
        print "ESC - back"

        self.selected = selected
        self.command = None
        self.drag = None

    def handle_key(self, ev):
        if ev.key == K_ESCAPE:
            self.change(MainState)
        if self.selected is None:
            return
        if ev.key == K_f:
            s = raw_input("New fill color (r,g,b,a or 0 for none)=")
            if s == "":
                return
            if s == "0":
                self.selected.shape.fillcolor(None)
            else:
                try:
                    t = eval(s)
                    self.selected.shape.fillcolor(*t)
                except:
                    print "invalid color"
                    return
            self.selected.shape.compile()

class CreateState(State):
    def enter(self, type=None):
        self.type = type
        self.points = []

    def handle_key(self, ev):
        if ev.key == K_ESCAPE:
            self.change(MainState)
        if self.type == 'poly' and ev.key == K_BACKSPACE:
            if self.points:
                self.points.pop()                
        if self.type is not None:
            return
        if ev.key == K_r:
            self.type = 'rect'
            print "\nCreating rectangle, select top left point"
        elif ev.key == K_c:
            self.type = 'circle'
            print "\nCreating circle, select center point"
        elif ev.key == K_p:
            self.type = 'poly'
            print "\nCreating polygon, right click finishes"

    def handle_click(self, ev):
        if self.type is None:
            return
        pts = self.points
        mpos = pygame.mouse.get_pos()

        shape = None
        if ev.button == 3:
            if self.type == 'poly':
                shape,cx,cy = self._get_shape(pts + [mpos])
            else:
                return
        pts.append(mpos)
        lp = len(pts)
        if lp == 2:
            if self.type in ('rect', 'circle'):
                shape,cx,cy = self._get_shape(pts)
        if shape is not None:
            if self.editor.fillcolor is not None:
                shape.fillcolor(*self.editor.fillcolor)
            if self.editor.linecolor is not None:
                shape.linecolor(*self.editor.linecolor)
            self.editor.shapes.append(EditorObject(shape, cx, cy))
            self.change(MainState)
                

    def render(self):
        if self.type is None or not self.points:
            return
        pts = self.points
        mx,my = pygame.mouse.get_pos()
        shape,cx,cy = self._get_shape(pts + [(mx,my)])
        shape.linecolor(255,255,255,125).linewidth(2)
        draw_shape(shape, cx, cy)
            

    def _get_shape(self, pts):        
        if self.type == 'rect':
            x,y = pts[0]
            xx,yy = pts[1]
            cx,cy = (x+xx)/2.0, (y+yy)/2.0
            shape = rect(abs(x-xx),abs(y-yy))
        elif self.type == 'circle':
            cx,cy = pts[0]
            xx,yy = pts[1]
            radius = math.sqrt((cx-xx)**2+(cy-yy)**2)
            shape = circle(radius)
        elif self.type == 'poly':
            shape = poly(pts)
            try:
                cx,cy = shape._polygon.center()
            except:
                cx,cy = pts[0]
            shape._polygon.shift(-cx,-cy)
        return shape,cx,cy            
            

if __name__ == '__main__':
    Editor().mainloop()
