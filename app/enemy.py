import time
import random

import pygame

from .missiles import MIRV
from . import settings

class ReplayUnit:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x,y,50,50)
     
class Enemy:
    def __init__(self, towers, cities, groups):
        self.targets = [tower for tower in towers]
        self.targets.extend([city for city in cities])

        self.groups = groups.copy()
        self.icbm_group = self.groups.pop('enemy')
        self.mirv_idx = []
        self.t1 = pygame.time.get_ticks()
        self.color = 'red'
        self.speed = 0

    def replay(self, data):
        x, y = data['target']
        target = ReplayUnit(x,y)
        icbm = MIRV(data['start'], target, self.groups, self.color, self.speed, data['split'], self.mirv)
        self.icbm_group.add(icbm)
        
    def fire_missile(self, mirv=False, pos=None, salvo=False):
        split = False
        if mirv:
            start = (pos.x, pos.y)
            target = self.get_target()
            while target in self.mirv_idx:
                target = self.get_target()
            self.mirv_idx.append(target)
        else:
            target = self.get_target()
            start_x = random.randint(20, settings.SCREEN_WIDTH-20)
            start = (start_x, 50)
            if salvo == False:
                val = random.randint(0, 4)
                split = True if val == 0 else False

        icbm = MIRV(start, target, self.groups, self.color, self.speed, split, self.mirv)
        self.icbm_group.add(icbm)

    def mirv(self, pos):
        self.mirv_idx = []
        for i in range(3):
            self.fire_missile(mirv=True, pos=pos)

    def fire_salvo(self):
        for i in range(4):
            self.fire_missile(salvo=True)

    def get_target(self):
        # Check if target is alive, else re-roll target
        target_idx = random.randint(0, len(self.targets)-1)
        while self.targets[target_idx].alive == False:
            target_idx = random.randint(0, len(self.targets)-1)

        return self.targets[target_idx]

    def update(self):
        # add len(self.icbm_group) < n to limit number of missiles on screen
        #jitter = random.randint(-225, 225)
        if pygame.time.get_ticks() - self.t1 > 2000: #+ jitter:
            self.fire_missile()
            self.t1 = pygame.time.get_ticks()











#
