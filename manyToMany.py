#! /usr/bin/env python

import os
import random
import pygame
from pygame.locals import *
import math
import sys
import numpy as np
import tensorflow as tf
import random
import enum

os.environ["SDL_VIDEO_CENTERED"] = "1"
point_states = {'flow','travel'}
SCREEN_SIZE = 600
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Politics Game: Data Display")
radius = SCREEN_SIZE/2*0.6
center = tf.convert_to_tensor([SCREEN_SIZE/2, SCREEN_SIZE/2])

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
    return tf.convert_to_tensor([tf.sin(angle), tf.cos(angle)])

def reflectNorm(current_direction, normal):
    mag = tf.linalg.norm(normal)
    projection = tf.dot(current_direction, normal)/(mag**2)*normal
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
            x_pos = radius*thickness*tf.sin(rad) + center[0]
            y_pos = radius*thickness*tf.cos(rad) + center[1]
            outer_points += [[x_pos, y_pos]]
        for i in range(stop_angle, start_angle - 1, -step):
            rad = np.pi/180.0 * float(i)
            x_pos = radius*tf.sin(rad) + center[0]
            y_pos = radius*tf.cos(rad) + center[1]
            inner_points += [[x_pos, y_pos]]
        points = outer_points + inner_points + [outer_points[0]]
        return tf.convert_to_tensor(points)

    def drawText(self,screen):
        thickness = (0.9 + 1.1*self.thickness)/2.0
        interval = 2*np.pi/float(self.num_blocs)
        for bloc in range(self.num_blocs):
            text = self.bloc_text[bloc]
            rad = (bloc + 0.5)*interval
            x_pos = radius*thickness*tf.sin(rad) + center[0]
            y_pos = radius*thickness*tf.cos(rad) + center[1]
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
    def __init__(self, num_categories, category_names=None):
        if category_names == None:
            category_names = [f"Category_{i}" for i in range(num_categories)]
        self.num_categories = num_categories
        self.locations = tf.random.uniform(maxval=SCREEN_SIZE, shape=[num_categories,2])
        self.directions = tf.zeros(shape=(num_categories,2))
        # Give each category a random direction
        for category in range(num_categories):
            self.directions[category] += tf.convert_to_tensor(genUnitVector())
        self.colors = [genHue() for color in range(num_categories)]
        self.point_totals = [0 for _ in range(num_categories)]
        self.flow_rate = 0.1
        self.font = pygame.font.SysFont(None,18)
        self.category_text = [self.font.render(category_names[i], True, (0,0,0)) for i in range(num_categories)]
        self.collisions()

    def getNextId(self, category):
        probability = tf.convert_to_tensor([[0,4,1,1,1],
                                [1,0,1,1,1],
                                [1,4,0,1,1],
                                [1,4,1,0,1],
                                [1,4,1,1,0]])
        if category != -1:
            self.point_totals[category] -= 1
        loc_prob = probability[category]/sum(probability[category])
        new_category = tf.random.choice(self.num_categories, p=loc_prob)
        self.point_totals[new_category] += 1
        return new_category

    def getSize(self, category):
        return  tf.sqrt(self.point_totals[category]) * 3

    def getNextDest(self, point, category):
        location = point.getLocation()
        category = category
        size = self.getSize(category)
        flow_rate = self.flow_rate
        offset = genUnitVector()
        flow_probability =  tf.random.uniform()

        # Make the next point go to a new category, but don't trigger the flow
        # probability at the next destination
        travel_margin = 2
        if flow_probability < flow_rate and point.state == PointStates.FLOW:
            point.dest_num = self.getNextId(category)
            point.state = PointStates.TRAVEL
            offset = offset * travel_margin
        else:
            if point.state == PointStates.FLOW:
                offset = offset*tf.random.uniform()*size
            else:
                point.state = PointStates.FLOW
                offset = offset * travel_margin
        return self.locations[category] + offset

    def getColor(self, category):
        return self.colors[category]

    def drawText(self, screen):
        for cat in range(self.num_categories):
            text = self.category_text[cat]
            rect = text.get_rect()
            target_loc = self.locations[cat] - tf.convert_to_tensor([rect.width/2, rect.height/2])
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
                    cur_distance = tf.linalg.norm(cur_loc - other_loc)
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
            center_distance = tf.linalg.norm(normal)
            normal = normal/center_distance
            # If there is a collision:
            #   1. Move current particle outside of the collision range
            #   2. Apply collision physics to the direction of each particle
            if center_distance + cur_size >= radius:
                normal = normal*(center_distance + cur_size - radius)*marg
                cur_loc += normal
                reflectNorm(self.directions[category], normal)

    def updateLocations(self, screen):
        self.collisions()
        speed = 0.2
        self.locations += self.directions*speed
        self.drawText(screen)

################################################################################
# An enum for point states
class PointStates(enum.Enum):
    FLOW = 0
    TRAVEL = 1

################################################################################
# A class for particle system categories.
class DataPoint(object):
    def __init__(self, dest_type):
        self.rect = pygame.rect.Rect((2, 2, 4, 4))
        self.dest = self.getLocation()
        self.color = genHue()
        self.dest_type = dest_type
        self.dest_num = dest_type.getNextId(-1)
        self.state = PointStates.FLOW

    def getLocation(self):
        return tf.convert_to_tensor(self.rect.center)

    def draw(self, surface):
        location = self.getLocation()
        direction = self.dest - location
        close_detect = tf.sum(tf.abs(direction))
        max_speed = 3
        if close_detect > 2*max_speed:
            if close_detect > self.dest_type.getSize(self.dest_num):
                max_speed = 8
            direction = max_speed/close_detect*direction

        self.rect.move_ip(round(direction[0]), round(direction[1]))
        pygame.draw.rect(screen, self.color, self.rect)
        return close_detect < 1

################################################################################
# A class for displaying voter data.
class VoterDataDisplay(object):
    def __init__(self):
        self.blocs = BlockDisplay(24)
        self.categories = Categories(5)
        self.categories.collisions()
        num_points = 1000
        self.points = [DataPoint(self.categories) for _ in range(num_points)]

    def updatePoints(self, screen):
        for point in self.points:
            arrived = point.draw(screen)
            if arrived:
                if type(point.dest_type) == Categories:
                    if point.state == PointStates.FLOW:
                        point.color = self.categories.getColor(point.dest_num)
                    point.dest = self.categories.getNextDest(point, point.dest_num)

    def draw(self, screen):
        self.categories.flow_rate = max(0.01, 0.15 * tf.sin(pygame.time.get_ticks()*2*np.pi/1000/10))
        self.updatePoints(screen)
        self.blocs.updateBlocDisplay(screen)
        self.categories.updateLocations(screen)

def renderGraphics():
    pygame.init()
    clock = pygame.time.Clock()
    running = True
    voter_data = VoterDataDisplay()
    text = 'this text is editable'
    font = pygame.font.SysFont(None, 48)
    img = font.render(text, True, (0,0,0))

    rect = img.get_rect()
    rect.topleft = (20, 20)
    cursor = Rect(rect.topright, (3, rect.height))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
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
        voter_data.draw(screen)
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
