import time
import random

import pygame

from .settings import DIR
from .missiles import ABM
  
KEYBINDS = (pygame.K_a, pygame.K_s, pygame.K_d)
TOWER_LOCS = [(20,580), (600, 580), (1180, 580)] #585

ABM_SHAPE = [
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 1, 0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1, 0, 1],
]

# -- HELPER
def make_abms(tower):
    abms = []
    for row_idx, row in enumerate(ABM_SHAPE):
        for cell_idx, cell in enumerate(row):
            if cell == 1:
                rect = pygame.Rect((5+10*cell_idx, 5+15*row_idx, 10, 10))
                abms.append(rect)
    return abms

class Tower:
    def __init__(self, x, y):
        self.surface = pygame.Surface((80,70)).convert()
        self.rect = self.surface.get_rect(topleft=(x,y))
        self.surface.fill('grey')
        self.color = 'blue'
        self.build()

        self.fire_sound = pygame.mixer.Sound(f'{DIR}/assets/fire.wav')
        self.fire_sound.set_volume(0.20)
        self.empty_sound = pygame.mixer.Sound(f'{DIR}/assets/empty.wav')
        self.empty_sound.set_volume(0.20)

    def build(self):
        self.alive = True
        self.abms = make_abms(self.rect)
        self.reload = {}
        self.dead_time = False

    def fire_missile(self, target, groups):
        if self.abms and target[1] < self.rect.top-10 and self.alive: #50
            rocket = ABM(self.rect.midtop, target, groups, color=self.color)

            groups['rocket'].add(rocket)

            self.reload[time.perf_counter()] = self.abms.pop()
            self.fire_sound.play()
        else:
            self.empty_sound.play()

    def kill(self):
        self.abms = []
        self.dead_time = time.perf_counter()

    def update(self):
        if self.reload and self.dead_time == False:
            keys = list(self.reload.keys())
            for t1 in keys:
                t2 = time.perf_counter()
                if t2 - t1 > 5:
                    self.abms.append(self.reload.pop(t1))

        elif self.dead_time:
            if time.perf_counter() - self.dead_time > 5:
                self.build()

    def draw(self, surface):
        self.surface.fill('grey')
        for abm in self.abms:
            pygame.draw.rect(self.surface, 'black', abm)

        surface.blit(self.surface, self.rect)

class City:
    def __init__(self, rect, color='cyan'):
        self.alive = True
        self.rect =  rect
        self.color = color
  
    def kill(self):
        self.alive = False

    def draw(self, surface):
        if self.alive:
            pygame.draw.rect(surface, self.color, self.rect)


class Player:
    def __init__(self, groups):
        self.towers = {key: Tower(loc[0], loc[1]) for key, loc in zip(KEYBINDS, TOWER_LOCS)}
        self.cities = [City(pygame.Rect((160+i*150, 600, 50, 50))) for i in range(3)]
        self.cities.extend([City(pygame.Rect((760+i*150, 600, 50, 50))) for i in range(3)])
        self.extra_city = 0
        self.score = 0
        self.accumulator = 0

        self.groups = groups
        
        self.city_sound = pygame.mixer.Sound(f'{DIR}/assets/extracity.wav')
        self.city_sound.set_volume(0.20)

    def replay(self, data):
        self.towers[int(data['key'])].fire_missile(data['pos'], self.groups)
        
    def score_up(self, val):
        self.score += val
        self.accumulator += val

        if self.accumulator >= 7000:
            while self.accumulator >= 7000:
                self.extra_city += 1
                self.city_sound.play()
                self.accumulator -= 7000

    def input(self, event):
        if event.key in KEYBINDS:
            mx, my = pygame.mouse.get_pos()
            self.towers[event.key].fire_missile((mx, my), self.groups)

    def update(self):
        for tower in self.towers.values():
            tower.update()

    def draw(self, surface):
        for tower in self.towers.values():
            tower.draw(surface)

        for city in self.cities:
            city.draw(surface)


# eof
