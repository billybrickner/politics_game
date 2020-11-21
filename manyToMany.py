#! /usr/bin/env python

import os
import random
import pygame
import math
import sys
import numpy as np
import random

os.environ["SDL_VIDEO_CENTERED"] = "1"

SCREEN_SIZE = 600
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("LEVEL 2 = Find the Correct Square!")

clock = pygame.time.Clock()

def genHSLColor():
    triangle = np.random.randint(3)
    randScale = np.random.rand()
    if triangle == 0:
        return (255*(1-randScale), 255*randScale, 0)
    if triangle == 1:
        return (0, 255*(1-randScale), 255*randScale)
    if triangle == 2:
        return (255*randScale, 0, 255*(1-randScale))

class Categories(object):
    def __init__(self, num_categories, num_points):
        self.num_categories = num_categories
        self.locations = np.random.uniform(0, SCREEN_SIZE, size=(num_categories,2))
        self.directions = np.zeros(shape=(num_categories,2))
        for cat in range(num_categories):
            angle = 2*np.pi*np.random.rand()
            self.directions[cat][0] = np.sin(angle)
            self.directions[cat][1] = np.cos(angle)
        self.colors = [genHSLColor() for color in range(num_categories)]
        self.point_totals = [0 for _ in range(num_categories)]
        self.points = [DataPoint(self) for _ in range(num_points)]
        self.threshold = 0.2

    def getCategory(self, init=False):
        cat = np.random.randint(self.num_categories)
        if init:
            self.point_totals[cat] += 1
        return cat

    def getArea(self, category):
        return  self.point_totals[category]/5

    def getNextDest(self, category, location):
        area = self.getArea(category)
        thresh = self.threshold
        angle = np.random.rand()*2*np.pi
        offset = np.array([np.sin(angle), np.cos(angle)])
        if np.linalg.norm(location - self.locations[category])/area < thresh:
            category = self.getCategory()
            offset = offset*thresh*area*1.2
        else:
            offset = offset*np.random.rand()*area
        return (self.locations[category] + offset, category)

    def getColor(self, category):
        return self.colors[category]

    def reflectNorm(self, category, normal):
        current_direction = self.directions[category]
        mag = np.linalg.norm(normal)
        projection = np.dot(current_direction, normal)/(mag**2)*normal
        current_direction -= 2*projection

    def collisions(self):
        for category in range(self.num_categories):
            cur_loc = self.locations[category]
            cur_area = self.getArea(category)
            # Check collision with other category areas
            for otherCat in range(self.num_categories):
                if otherCat != category:
                    other_loc = self.locations[otherCat]
                    other_area = self.getArea(otherCat)
                    cur_distance = np.linalg.norm(cur_loc - other_loc)
                    exp_distance = cur_area +  other_area
                    if cur_distance <= exp_distance:
                        mov_dir = cur_loc - other_loc
                        cur_loc += mov_dir/cur_distance*(exp_distance-cur_distance)*1.01
                        self.reflectNorm(category, cur_loc - other_loc)
                        self.reflectNorm(otherCat, other_loc - cur_loc)
            if cur_loc[0] <= cur_area:
                cur_loc[0] = cur_area*1.01
                self.reflectNorm(category, np.array([1,0]))
            if cur_loc[0] + cur_area >= SCREEN_SIZE:
                cur_loc[0] = SCREEN_SIZE - cur_area*1.01
                self.reflectNorm(category, np.array([-1,0]))
            if cur_loc[1] <= cur_area:
                cur_loc[1] = cur_area*1.01
                self.reflectNorm(category, np.array([0,1]))
            if cur_loc[1] + cur_area >= SCREEN_SIZE:
                cur_loc[1] = SCREEN_SIZE - cur_area*1.01
                self.reflectNorm(category, np.array([0,-1]))

    def updateLocations(self, screen):
        self.threshold = max(0.01, 0.15 * np.sin(pygame.time.get_ticks()*2*np.pi/1000/10))
        self.collisions()
        for cat in range(self.num_categories):
            speed = 0.5
            direction = self.directions[cat]
            new_loc = self.locations[cat] + direction*speed
            for i in range(len(self.locations[cat])):
                self.locations[cat][i] = new_loc[i]
        for point in self.points:
            point.draw(screen)

class DataPoint(object):
    def __init__(self, categories):
        self.rect = pygame.rect.Rect((2, 2, 4, 4))
        self.dest = np.array([self.rect.x, self.rect.y])
        self.gridSize = 24
        self.categories = categories
        self.category = categories.getCategory(init=True)
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
        loc = np.array([self.rect.x, self.rect.y])
        direction = self.dest - loc
        mag = np.linalg.norm(direction)
        if (mag < 1):
            self.color = self.categories.getColor(self.category)
            self.dest, self.category = self.categories.getNextDest(self.category, loc)
        max_speed = 3
        if mag > 2*max_speed:
            direction = max_speed/mag*direction
        self.rect.move_ip(round(direction[0]), round(direction[1]))
        pygame.draw.rect(screen, self.color, self.rect)

def main():
    pygame.init()


    clock = pygame.time.Clock()

    running = True
    categories = Categories(9, 1500)

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
