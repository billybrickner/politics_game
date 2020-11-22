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

clock = pygame.time.Clock()

################################################################################
# Generate a random hue
def genHue():
    triangle = np.random.randint(3)
    randScale = np.random.rand()
    if triangle == 0:
        return (255*(1-randScale), 255*randScale, 0)
    if triangle == 1:
        return (0, 255*(1-randScale), 255*randScale)
    if triangle == 2:
        return (255*randScale, 0, 255*(1-randScale))

def genUnitVector():
    angle = (2*np.pi)*np.random.rand()
    return np.array([np.sin(angle), np.cos(angle)])

def reflectNorm(current_direction, normal):
    mag = np.linalg.norm(normal)
    projection = np.dot(current_direction, normal)/(mag**2)*normal
    current_direction -= 2*projection

################################################################################
# A class for particle system categories.
class Categories(object):
    def __init__(self, num_categories, num_points, category_names=None):
        if category_names == None:
            category_names = [f"Category{i}" for i in range(num_categories)]
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

    def drawText(self):
        for cat in range(self.num_categories):
            text = self.category_text[cat]
            rect = text.get_rect()
            target_loc = self.locations[cat] - np.array([rect.width/2, rect.height/2])
            screen.blit(text, target_loc)

    def collisions(self):
        radius = SCREEN_SIZE/2*0.6
        center = np.array([SCREEN_SIZE/2, SCREEN_SIZE/2])
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
        self.drawText()

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

def main():
    pygame.init()
    clock = pygame.time.Clock()
    running = True
    categories = Categories(5, 1500)
    player = DataPoint(categories)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
                running = False
            if event.type == pygame.KEYDOWN:
                player.handle_keys()

        screen.fill((255, 255, 255))

        player.draw(screen)
        categories.updateLocations(screen)
        pygame.display.update()
        clock.tick(40)
main()
