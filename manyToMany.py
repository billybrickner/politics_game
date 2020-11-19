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

class Catagories(object):
    def __init__(self, num_catagories):
        self.num_catagories = num_catagories
        self.locations = np.random.randint(SCREEN_SIZE, size=(num_catagories,2))
        self.destinations = np.copy(self.locations)
        self.colors = [genHSLColor() for color in range(num_catagories)]

    def getCatagory(self):
        return np.random.randint(self.num_catagories)

    def getNextDest(self, catagory):
        area = 80
        if np.random.rand() < 0.01:
            catagory = self.getCatagory()
        angle = np.random.rand()*2*np.pi
        offset = np.array([np.sin(angle), np.cos(angle)])
        offset = offset*area*np.random.rand()
        return (self.locations[catagory] + offset, catagory)

    def getColor(self, catagory):
        return self.colors[catagory]

    def updateLocations(self):
        for cat in range(self.num_catagories):
            speed = 1
            direction = self.destinations[cat] - self.locations[cat]
            mag = np.linalg.norm(direction)
            #print(cat,mag)
            if mag > 10:
                self.locations[cat] = self.locations[cat] + direction/mag*speed
            else:
                print("BEFORE", self.destinations[cat])
                self.destinations[cat] = np.random.randint(SCREEN_SIZE, size=(2))
                print("AFTER", self.destinations[cat])

class DataPoint(object):
    def __init__(self, catagories):
        self.rect = pygame.rect.Rect((2, 2, 10, 10))
        self.dest = np.array([self.rect.x, self.rect.y])
        self.gridSize = 24
        self.catagories = catagories
        self.catagory = catagories.getCatagory()
        self.color = catagories.getColor(self.catagory)

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
        if (mag > 1):
            max_speed = 5
            if mag > 2*max_speed:
                direction = max_speed/mag*direction
            self.rect.move_ip(round(direction[0]), round(direction[1]))
        else:
            self.color = self.catagories.getColor(self.catagory)
            self.dest, self.catagory = self.catagories.getNextDest(self.catagory)
        pygame.draw.rect(screen, self.color, self.rect)

def main():
    pygame.init()


    clock = pygame.time.Clock()

    running = True
    catagories = Catagories(5)

    player = DataPoint(catagories)

    points = [DataPoint(catagories) for _ in range(4000)]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
                running = False
            if event.type == pygame.KEYDOWN:
                player.handle_keys()

        screen.fill((255, 255, 255))

        player.draw(screen)
        for point in points:
            point.draw(screen)
        pygame.display.update()
        catagories.updateLocations()
        clock.tick(40)
main()
