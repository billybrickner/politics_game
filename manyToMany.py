#! /usr/bin/env python

import os
import random
import pygame
from pygame.locals import *
import math
import sys
import numpy as np
import random

os.environ["SDL_VIDEO_CENTERED"] = "1"

SCREEN_SIZE = 600
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Politics Game: Data Display")
radius = SCREEN_SIZE/2*0.6
center = np.array([SCREEN_SIZE/2, SCREEN_SIZE/2])

clock = pygame.time.Clock()

################################################################################
# Generate a random hue
def genHue():
    sector = np.random.randint(4)
    randScale = np.random.rand()
    blue_buf = 0.6
    if sector == 0:
        return (255*randScale, 255, 0)
    if sector == 1:
        return (255, 0, 255*randScale)
    if sector == 2:
        return (255*randScale, 255, 0)
    if sector == 3:
        return (0, 255, 255*randScale)
    '''if sector == 4:
        return (0, 255*(1 - blue_buf*randScale), 255)
    if sector == 5:
        return (255*(1 - blue_buf*randScale), 0, 255)
    '''

def genUnitVector():
    angle = (2*np.pi)*np.random.rand()
    return np.array([np.sin(angle), np.cos(angle)])

def reflectNorm(current_direction, normal):
    mag = np.linalg.norm(normal)
    projection = np.dot(current_direction, normal)/(mag**2)*normal
    current_direction -= 2*projection

################################################################################
# A class for bloc particle systems
class BlockDisplay(object):
    def __init__(self, num_blocs, bloc_names=None, thickness = 1.4):
        self.num_blocs = num_blocs
        if bloc_names == None:
            bloc_names = [f"Bloc_{i}" for i in range(num_blocs)]
        self.bloc_names = bloc_names
        self.thickness = thickness
        angle_div = 360.0/float(num_blocs)
        self.polygons = [self.make_ring(angle_div*i, angle_div*(i+1),360/num_blocs) for i in range(num_blocs)]
        self.hues = [genHue() for _ in range(num_blocs)]
        self.font = pygame.font.SysFont(None,18)
        self.bloc_text = [self.font.render(bloc_names[i], True, (0,0,0)) for i in range(num_blocs)]

    def make_ring(self, start_angle, stop_angle, step=1):
        if stop_angle < start_angle:
            start_angle, stop_angle = stop_angle, start_angle
        thickness = self.thickness
        start_angle = int(start_angle)
        stop_angle = int(stop_angle)
        outer_points = []
        inner_points = []
        step = int(step)
        for i in range(start_angle, stop_angle + 1, step):
            rad = np.pi/180.0 * float(i)
            x_pos = radius*thickness*np.sin(rad) + center[0]
            y_pos = radius*thickness*np.cos(rad) + center[1]
            outer_points += [[x_pos, y_pos]]
        for i in range(stop_angle, start_angle - 1, -step):
            rad = np.pi/180.0 * float(i)
            x_pos = radius*np.sin(rad) + center[0]
            y_pos = radius*np.cos(rad) + center[1]
            inner_points += [[x_pos, y_pos]]
        points = outer_points + inner_points + [outer_points[0]]
        return np.array(points)

    def drawText(self,screen):
        thickness = (0.9 + 1.1*self.thickness)/2.0
        interval = 2*np.pi/float(self.num_blocs)
        for bloc in range(self.num_blocs):
            text = self.bloc_text[bloc]
            rad = (bloc + 0.5)*interval
            x_pos = radius*thickness*np.sin(rad) + center[0]
            y_pos = radius*thickness*np.cos(rad) + center[1]
            rect = text.get_rect()
            x_pos -= rect.width/2
            y_pos -= rect.height/2
            target_loc = [x_pos, y_pos]
            screen.blit(text, target_loc)


    def updateBlocDisplay(self, screen):
        for polygon, hue in zip(self.polygons, self.hues):
            pygame.draw.polygon(screen, hue, polygon)
        self.drawText(screen)

################################################################################
# A class for particle system categories.
class Categories(object):
    def __init__(self, num_categories, num_points, category_names=None):
        if category_names == None:
            category_names = [f"Category_{i}" for i in range(num_categories)]
        self.num_categories = num_categories
        self.locations = np.random.uniform(0, SCREEN_SIZE, size=(num_categories,2))
        self.directions = np.zeros(shape=(num_categories,2))
        # Give each category a random direction
        for category in range(num_categories):
            self.directions[category] += genUnitVector()
        self.colors = [genHue() for color in range(num_categories)]
        self.point_totals = [0 for _ in range(num_categories)]
        self.points = [DataPoint(self) for _ in range(num_points)]
        self.flow_rate = 0.1
        self.font = pygame.font.SysFont(None,18)
        self.category_text = [self.font.render(category_names[i], True, (0,0,0)) for i in range(num_categories)]

    def getCategory(self, category):
        probability = np.array([[0,4,1,1,1],
                                [1,0,1,1,1],
                                [1,4,0,1,1],
                                [1,4,1,0,1],
                                [1,4,1,1,0]])
        if category == -1:
            new_category = np.random.randint(self.num_categories)
            self.point_totals[new_category] += 1
        else:
            loc_prob = probability[category]/sum(probability[category])
            new_category = np.random.choice(self.num_categories, p=loc_prob)
            self.point_totals[category] -= 1
            self.point_totals[new_category] += 1
        return new_category

    def getSize(self, category):
        return  np.sqrt(self.point_totals[category]) * 3

    def getNextDest(self, point, location):
        category = point.category
        size = self.getSize(category)
        flow_rate = self.flow_rate
        offset = genUnitVector()
        # The probability is calculated based on the probability of dot being a
        # particular distance from the center
        flow_probability =  np.linalg.norm(location - self.locations[category])/size
        # Make the next point go to a new category, but don't trigger the flow
        # probability at the next destination
        flow_margin = 1.01
        if flow_probability < flow_rate:
            category = self.getCategory(category)
            offset = offset*size*(flow_rate*flow_margin)
        else:
            # The random value for deciding the flow probability is chosen here
            # The effect is that points close to the center get sent to other
            # categories
            offset = offset*np.random.rand()*size
        point.category = category
        return self.locations[category] + offset

    def getColor(self, category):
        return self.colors[category]

    def drawText(self, screen):
        for cat in range(self.num_categories):
            text = self.category_text[cat]
            rect = text.get_rect()
            target_loc = self.locations[cat] - np.array([rect.width/2, rect.height/2])
            screen.blit(text, target_loc)

    def collisions(self):
        marg = 1.01     # Margin to separate collision
        closer = 0.9    # Make collisions where there is more point density
        for category in range(self.num_categories):
            cur_loc = self.locations[category]  # Current Location
            cur_size = self.getSize(category)   # Current Size
            # Check collision with other category sizes
            for otherCat in range(category, self.num_categories):
                if otherCat != category:
                    other_loc = self.locations[otherCat]
                    other_size = self.getSize(otherCat)
                    cur_distance = np.linalg.norm(cur_loc - other_loc)
                    exp_distance = (cur_size +  other_size) * closer
                    # If there is a collision:
                    #   1. Move current particle outside of the collision range
                    #   2. Apply collision physics to the direction of each particle
                    if cur_distance <= exp_distance:
                        mov_dir = cur_loc - other_loc
                        cur_loc += mov_dir/cur_distance*(exp_distance-cur_distance)*marg
                        reflectNorm(self.directions[category], cur_loc - other_loc)
                        reflectNorm(self.directions[otherCat], other_loc - cur_loc)
            normal = center - cur_loc
            center_distance = np.linalg.norm(normal)
            normal = normal/center_distance
            # If there is a collision:
            #   1. Move current particle outside of the collision range
            #   2. Apply collision physics to the direction of each particle
            if center_distance + cur_size >= radius:
                normal = normal*(center_distance + cur_size - radius)*marg
                cur_loc += normal
                reflectNorm(self.directions[category], normal)

    def updateLocations(self, screen):
        self.flow_rate = max(0.01, 0.15 * np.sin(pygame.time.get_ticks()*2*np.pi/1000/10))
        self.collisions()
        speed = 0.2
        self.locations += self.directions*speed
        for point in self.points:
            point.draw(screen)
        self.drawText(screen)

class DataPoint(object):
    def __init__(self, categories):
        self.rect = pygame.rect.Rect((2, 2, 4, 4))
        self.dest = np.array([self.rect.x, self.rect.y])
        self.categories = categories
        self.category = categories.getCategory(-1)
        self.color = categories.getColor(self.category)

    def handle_keys(self):
        key = pygame.key.get_pressed()
        dist = 1
        if key[pygame.K_a]:
            self.dest[0] -= self.gridSize
        if key[pygame.K_d]:
            self.dest[0] += self.gridSize
        if key[pygame.K_w]:
            self.dest[1] -= self.gridSize
        if key[pygame.K_s]:
            self.dest[1] += self.gridSize
        if key[pygame.K_q]:
            pygame.quit()
            sys.exit()

    def draw(self, surface):
        location = np.array([self.rect.x, self.rect.y])
        direction = self.dest - location
        mag = np.linalg.norm(direction)
        if (mag < 1):
            self.color = self.categories.getColor(self.category)
            self.dest = self.categories.getNextDest(self, location)
        max_speed = 3
        if mag > 2*max_speed:
            if mag > self.categories.getSize(self.category):
                max_speed = 8
            direction = max_speed/mag*direction
        self.rect.move_ip(round(direction[0]), round(direction[1]))
        pygame.draw.rect(screen, self.color, self.rect)

def renderGraphics():
    pygame.init()
    clock = pygame.time.Clock()
    running = True
    categories = Categories(5, 1500)
    player = DataPoint(categories)
    text = 'this text is editable'
    font = pygame.font.SysFont(None, 48)
    img = font.render(text, True, (0,0,0))

    rect = img.get_rect()
    rect.topleft = (20, 20)
    cursor = Rect(rect.topright, (3, rect.height))
    blocs = BlockDisplay(24)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == K_BACKSPACE:
                    if len(text)>0:
                        text = text[:-1]
                else:
                    text += event.unicode
                img = font.render(text, True, (0,0,0))
                rect.size=img.get_size()
                cursor.topleft = rect.topright
        screen.fill((255, 255, 255))
        screen.blit(img, rect)
        blocs.updateBlocDisplay(screen)
        player.draw(screen)
        categories.updateLocations(screen)
        if pygame.time.get_ticks()%1000 > 500:
            pygame.draw.rect(screen, (0,0,0), cursor)
            if len(text) > 1 and text[-1] == ".":
                try:
                    eval(f"main.{text[:-1]}")
                except Exception as e:
                    print(e)
        pygame.display.update()
        clock.tick(40)

renderGraphics()
