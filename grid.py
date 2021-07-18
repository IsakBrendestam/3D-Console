import pygame
import numpy as np
import random

class Grid:
    def __init__(self, width, height, scale, offset):
        self.scale = scale
        self.columns = int(height/2)
        self.rows = int(width/2)
        self.size = (self.rows, self.columns)
        self.grid_array = np.ndarray(shape=(self.size))
        self.offset = offset

    def generate_random_2D_array(self):
        for x in range(self.rows):
            for y in range(self.columns):
                self.grid_array[x][y] = random.randint(0, 1)
        
    def draw_two_colors(self, off_color, on_color, surface):
        for x in range(self.rows):
            for y in range(self.columns):
                x_pos = self.scale*x
                y_pos = self.scale*y

                if self.grid_array[x][y] == 1:
                    pygame.draw.rect(surface, on_color, [x_pos, y_pos, self.scale-self.offset, self.scale-self.offset])
                else:
                    pygame.draw.rect(surface, off_color, [x_pos, y_pos, self.scale-self.offset, self.scale-self.offset])

    def draw_luminance(self, position, max_lumnance, surface):
        x_pos = self.scale*position[0]
        y_pos = self.scale*position[1]
        luminance = position[2]/max_lumnance
        color_value = 255*luminance
        color = (color_value, color_value, color_value)
        pygame.draw.rect(surface, color, [x_pos, y_pos, self.scale-self.offset, self.scale-self.offset])