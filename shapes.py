"""
Working 2021-02-10
"""
import os
import numpy as np
import curses
import time
import keyboard
import pygame
from pygame.constants import WINDOWSIZECHANGED
from grid import Grid
from math import pi, sin, cos
from enum import Enum, auto

class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

class State(AutoName):
    CONSOLE = auto()
    RENDER = auto()
    PICTURE = auto()

class Shape:
    """General class for ploting shape in terminal"""

    def __init__(self):
        self.window_width = os.get_terminal_size()[0]
        self.window_height = os.get_terminal_size()[1]
        self.CHARACTERS = ".,-~:;=!*#$@"

    def get_width(self)->int:
        return self.window_width
    
    def get_height(self)->int:
        return self.window_height

    def deg_to_rad(self, degrees:int)->int:
        """converts degrees to radians"""
        return (degrees*np.pi)/180
               
    def print_char(self, x:int, y:int, char:chr, screen)->None:
        """prints character at given position"""
        screen.addstr(*(y, x), char)

    def generate_buffer(self, value:int)->dict:
        """Generates a dictionary with keys for every pixel"""
        dic = {}
        for x in range(self.window_width):
            for y in range(self.window_height):
                dic[(x, y)] = value

        return dic

    def draw_shape_console(self, points:list, screen)->None:
        """Draws every point with a shade in the console"""
        for point in points: 
            self.print_char(point[0], point[1], self.CHARACTERS[point[2]], screen)    

    def draw_shape(self, points:list, some_grid:list, surface)->None:
        """Draws every point with a shade in the pygame window"""
        for point in points:
            some_grid.draw_luminance(point, len(self.CHARACTERS), surface)

class Cube(Shape):
    """Generates every point needed to draw a cube in 2D space"""

    def __init__(self, control_rotation = False):
        super().__init__()

        self.window_width = super().get_width()
        self.window_height = super().get_height()

        self.pos_x = self.window_width/2
        self.pos_y = self.window_height/2
        
        self.rot_y = 90
        self.rot_x = 90
        self.rot_z = 90

        self.length = 20

        self.distance = 40

        self.cos_A = 0
        self.sin_A = 0
        
        self.cos_B = 0
        self.sin_B = 0

        self.cos_C = 0
        self.sin_C = 0

        self.z_buffer = {}

        self.K2 = 10
        self.K1 = (self.window_width*self.K2*3)/(4*self.length)

        self.characters = "@$#*!=;:~-,."

        self.control_rotation = control_rotation

    def update(self, screen):
        """Updates rotation"""
        if self.control_rotation:
            if keyboard.is_pressed('d'):
                self.rot_x -= 7
            if keyboard.is_pressed('a'):
                self.rot_x += 7
            if keyboard.is_pressed('w'):
                self.rot_y -= 7
            if keyboard.is_pressed('s'):
                self.rot_y += 7
            if keyboard.is_pressed('q'):
                self.rot_z -= 7
            if keyboard.is_pressed('e'):
                self.rot_z += 7
        else:
            self.rot_x += 3
            self.rot_y += 7
            self.rot_z += 2

        super().draw_shape(self.cube_generator(), self.characters, screen)

    def cube_generator(self):
        """Generates a cube and rotates it"""
        points = []

        self.cos_A = np.cos(super().deg_to_rad(self.rot_y))  
        self.sin_A = np.sin(super().deg_to_rad(self.rot_y))  

        self.cos_B = np.cos(super().deg_to_rad(self.rot_x))  
        self.sin_B = np.sin(super().deg_to_rad(self.rot_x))

        self.cos_C = np.cos(super().deg_to_rad(self.rot_z))  
        self.sin_C = np.sin(super().deg_to_rad(self.rot_z))


        self.z_buffer = super().generate_buffer(0)

        for z in range(int(-self.length/2), int(self.length/2)):
            if z == int(-self.length/2) or z == int(self.length/2)-1:
                for y in range(int(-self.length/2), int(self.length/2)):
                    for x in range(int(-self.length/2), int(self.length/2)):
                        point = self.cur_point(x, y, z)
                        if point:
                            points.append(point)
            else:
                for y in range(int(-self.length/2), int(self.length/2)):
                    if y == int(-self.length/2) or y == int(self.length/2)-1:
                        for x in range(int(-self.length/2), int(self.length/2)):
                            point = self.cur_point(x, y, z)
                            if point:
                                points.append(point)
                    else:
                        point1 = self.cur_point(int(self.length/2), y, z)
                        if point1:
                            points.append(point1)                                        

                        point2 = self.cur_point(int(-self.length/2), y, z)
                        if point2:
                            points.append(point2)
        return points

    def cur_point(self, x, y, z):     
        a = y*self.cos_A + z*self.sin_A

        x_value = (x*self.cos_B + a*self.sin_B)*self.cos_C + (x*self.sin_B - a*self.cos_B)*self.sin_C
        y_value = (x*self.cos_B + a*self.sin_B)*self.sin_C - (x*self.sin_B - a*self.cos_B)*self.cos_C
        z_value = self.K2 + (-1)*y*self.sin_A + z*self.cos_A + self.distance
        ooz = 1/z_value

        x_pos = int(self.pos_x + self.K1*ooz*x_value)
        y_pos = int(self.pos_y - self.K1*ooz*y_value) 

        luminance = abs(z/self.length)

        point = (x_pos, y_pos, int(luminance*(len(self.characters)-1)))

        if (x_pos > 0 and x_pos < self.window_width) and (y_pos > 0 and y_pos < self.window_height):
            if ooz > self.z_buffer[(x_pos, y_pos)]:
                self.z_buffer[(x_pos, y_pos)] = ooz
                return point

        return None

class Sphere(Shape):
    """Generates every point needed to draw a torus in 2D space"""

    def __init__(self, start_x = 0, start_y = 0, start_z = 0, start_rot_x = 0, start_rot_y = 0, control_rotation = False):
        super().__init__()

        self.window_width = super().get_width()
        self.window_height = super().get_height()

        self.radius = 2

        self.rot_x = start_rot_x
        self.rot_y = start_rot_y
        
        self.K2 = 10
        self.K1 = (self.window_width*self.K2*3)/(8*(self.radius))

        self.pos_x = os.get_terminal_size()[0]/2 + start_x
        self.pos_y = os.get_terminal_size()[1]/2 + start_y

        self.control = control_rotation

        self.distance = 14 + abs(start_z)

        self.buffer = self.generate_buffer(0)
        
        self.characters = "@$#*!=;:~-,."

    def update(self, screen):
        """Updates rotation"""
        if self.control:
            if keyboard.is_pressed('d'):
                self.rot_x -= 7
            if keyboard.is_pressed('a'):
                self.rot_x += 7
            if keyboard.is_pressed('w'):
                self.rot_y -= 7
            if keyboard.is_pressed('s'):
                self.rot_y += 7
        else:
            self.rot_x += 3
            self.rot_y += 7

        super().draw_shape(self.sphere_generator(), self.characters, screen)

    def sphere_generator(self):
        """Generates circle, with calculated shading"""
        points = []

        z_buffer = super().generate_buffer(0)

        R1 = self.radius

        cos_A = np.cos(super().deg_to_rad(self.rot_y))  
        sin_A = np.sin(super().deg_to_rad(self.rot_y))  

        cos_B = np.cos(super().deg_to_rad(self.rot_x))  
        sin_B = np.sin(super().deg_to_rad(self.rot_x))
        
        #Makes cirkle that gets rot_yted
        for i in range(0, 180, 2):
            cos_i = np.cos(super().deg_to_rad(i))  
            sin_i = np.sin(super().deg_to_rad(i))   
         
            for j in range(0, 360, 2):
                cos_j = np.cos(super().deg_to_rad(j))   
                sin_j = np.sin(super().deg_to_rad(j))

                sphare_x = sin_i*cos_j
                sphare_y = sin_i*sin_j
                c = cos_i*cos_A
                
                x = R1*(sphare_x*cos_B + sin_B*(sphare_y*sin_A + c))
                y = R1*(sphare_y*cos_A - cos_i*cos_A)
                z = self.K2 + R1*((-1)*sphare_x*sin_B + cos_B*(sphare_y*sin_A + c)) + self.distance
                
                ooz = 1/z

                x_pos = int(self.pos_x + self.K1*ooz*x)
                y_pos = int(self.pos_y - self.K1*ooz*y)

                luminance = abs(sin_i)
                point = (x_pos, y_pos, int(luminance*(len(self.characters)-1)))

                if (x_pos > 0 and x_pos < self.window_width) and (y_pos > 0 and y_pos < self.window_height):
                    if ooz > z_buffer[(x_pos, y_pos)]:
                        z_buffer[(x_pos, y_pos)] = ooz
                        points.append(point)

        return points

class Torus(Shape):
    """Generates every point needed to draw a torus in 2D space"""

    def __init__(self, start_x:int=0, start_y:int=0, start_z:int=0, 
                 start_rot_x:int=0, start_rot_y:int=0, control_rotation:bool=False, 
                 window_size:tuple=None, detail_level = 90):
        super().__init__()

        self.window_width = super().get_width()
        self.window_height = super().get_height()

        if window_size:
            self.window_width = window_size[0]
            self.window_height = window_size[1]

        self.offset = 2
        self.radius = 1

        self.rot_x = start_rot_x
        self.rot_y = start_rot_y
        
        self.K2 = 10
        self.K1 = (self.window_width*self.K2*3)/(8*(self.offset + self.radius))

        self.pos_x = os.get_terminal_size()[0]/2 + start_x
        self.pos_y = os.get_terminal_size()[1]/2 + start_y

        self.control = control_rotation

        self.distance = abs(14 + start_z)

        self.buffer = super().generate_buffer(0)

        self.detail_level = 11 - int(detail_level/10)
        
    def update(self)->None:
        """Updates rotation"""
        if self.control:
            if keyboard.is_pressed('d'):
                self.rot_x -= 7
            if keyboard.is_pressed('a'):
                self.rot_x += 7
            if keyboard.is_pressed('w'):
                self.rot_y -= 7
            if keyboard.is_pressed('s'):
                self.rot_y += 7
        else:
            self.rot_x += 3
            self.rot_y += 7

    def torus_generator(self)->list:
        """Generates torus, with calculated shading"""
        points = []

        z_buffer = super().generate_buffer(0)

        R1, R2 = self.radius, self.offset

        angle_y = super().deg_to_rad(self.rot_y)
        cos_A, sin_A = cos(angle_y), sin(angle_y)  

        angle_x = super().deg_to_rad(self.rot_x)
        cos_B, sin_B = cos(angle_x), sin(angle_x) 

        #Agnle to rotate cirkle
        for i in range(0, 360, self.detail_level):
            angle_i = super().deg_to_rad(i)

            cos_i, sin_i = cos(angle_i), sin(angle_i)    
         
            circle_x = R2+R1*cos_i 
            circle_y = R1*sin_i

            #Angle to make cirkle
            for j in range(0, 360, self.detail_level):  
                angle_j = super().deg_to_rad(j)
                cos_j, sin_j = cos(angle_j), sin(angle_j)   

                x = circle_x * (cos_j*cos_B + sin_j*sin_A*sin_B) - (circle_y*cos_A*sin_B)
                y = circle_x * (cos_j*sin_B - sin_j*sin_A*cos_B) + (circle_y*cos_A*cos_B)
                z = self.K2 + cos_A*circle_x*sin_j + circle_y*sin_A + self.distance
                ooz = 1/z

                x_pos = int(self.pos_x + self.K1*ooz*x)
                y_pos = int(self.pos_y - self.K1*ooz*y)

                if (x_pos > 0 and x_pos < self.window_width) and (y_pos > 0 and y_pos < self.window_height):
                    if ooz > z_buffer[(x_pos, y_pos)]:
                        luminance = (cos_j*cos_i*sin_B) - (cos_A*cos_i*sin_j) - (sin_A*sin_i) + cos_B*(cos_A*sin_i - cos_i*sin_A*sin_j)
                        point = (x_pos, y_pos, abs(int(luminance*8)))
                        z_buffer[(x_pos, y_pos)] = ooz
                        points.append(point)

        return points


def main(screen, runState:State):
    """Function that runs the whole program"""

    #Shape declarations
    t1:Shape = Torus(start_x=-30)

    run = True
    
    if runState == State.CONSOLE:
        # -- Render shape in Console --

        #Curses setup
        curses.curs_set(0)
        screen.nodelay(True)
        
        #Global update-loop 
        while run:
            screen.erase()
            
            t1.update()
            t1.draw_shape_console(t1.torus_generator(), screen)
            #d2.update(screen)

            screen.refresh()
            time.sleep(0.01)

            if keyboard.is_pressed('c'):
                run = False

    elif runState == State.RENDER:
        # -- Render shape with pygame --

        os.environ['SDL_VIDEO_CENTERD']='1'

        width, height = 1200, 900
        size = (width, height)


        t1 = Torus(start_x=width/5 + 10, 
                   start_y=height/5 + 20,
                   start_z=-8,
                   window_size=(int(width/2), int(height/2)),
                   detail_level=20)

        pygame.init()
        pygame.display.set_caption('Shape render')
        screen = pygame.display.set_mode(size)
        clock = pygame.time.Clock()
        fps = 60

        black = (0, 0, 0)
        white = (255, 255, 255)

        scale = 2
        offset = 1

        temp_grid = Grid(width, height, scale, offset)

        while run:
            clock.tick(fps)
            screen.fill(black)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
            
            t1.update()
            t1.draw_shape(t1.torus_generator(), temp_grid, screen)

            pygame.display.update()

    elif runState == State.PICTURE:
        # -- Render a detailed picture with pygame --

        #Seting up rendering in pygamess
        os.environ['SDL_VIDEO_CENTERD']='1'

        width, height = 1200, 900
        size:tuple = (width, height)

        t1 = Torus(start_x=width/4 - 50, 
                   start_y=height/4 - 25,
                   start_rot_x=90, 
                   start_rot_y=45, 
                   window_size=(int(width/2), int(height/2)))

        pygame.init()
        pygame.display.set_caption('Shape render')
        screen = pygame.display.set_mode(size)
        clock = pygame.time.Clock()
        fps = 1

        black = (0, 0, 0)
        white = (255, 255, 255)

        scale = 2
        offset = 0

        screen.fill(black)

        temp_grid = Grid(width, height, scale, offset)

        t1.draw_shape(t1.torus_generator(), temp_grid, screen)

        pygame.display.update()

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
    

if __name__ == '__main__':
    curses.wrapper(main, State.CONSOLE)