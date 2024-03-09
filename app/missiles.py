import random

import pygame

from . import settings

DIR = settings.DIR
Vector = pygame.math.Vector2

def post_scoreup(unit):
    event_dict = {'usertype': 'scoreup', 'pos': unit.pos}
    evn = pygame.event.Event(pygame.USEREVENT, event_dict)
    success = pygame.event.post(evn)
    return

class Group:
    def __init__(self):
        self._group = []

    def __len__(self):
        return len(self._group)

    def __iter__(self):
        return iter(self._group)

    def add(self, unit):
        self._group.append(unit)

    def clear(self):
        self._group = []

    def update(self):
        new_group = []
        for member in self:
            if member.alive:
                new_group.append(member)
                member.update()
                
        self._group = new_group

    def draw(self, surface):
        for member in self:
            member.draw(surface)

class Missile:
    def __init__(self, start, target, color, speed, groups):
        self.alive = True
        self.start = Vector(start)
        self.pos = Vector(start)
        self.target = Vector(target)
        self.heading = (self.target - self.start).normalize()
        self.speed = speed
        self.color = color

        self.explosion_group = groups.get('explosion', [])
        self.collision_group = groups.get('enemy', [])
        self.killed_group = groups.get('kill', [])
        
        self.explosion_sound = pygame.mixer.Sound(f'{DIR}/assets/explosion.wav')
        self.explosion_sound.set_volume(0.20)
        
    def update(self):
        self.pos += self.heading * self.speed * 1/60

        if self.pos.distance_to(self.target) <= self.speed * 1/60:
            self.pos = self.target
            self.alive = False
            self.explosion_group.add(Explosion(self.pos, self.collision_group))
            self.explosion_sound.play()

    def draw(self, surface):
        pygame.draw.line(surface, self.color, self.start, self.pos, width=2)
        pygame.draw.rect(surface, (255,255,255),  (self.pos.x, self.pos.y, 1, 1))

class ABM(Missile):
    def __init__(self, start, target, groups={}, color='blue', speed=320):
        super().__init__(start, target, color, speed, groups)

        self.cross1a = (self.target.x-8, self.target.y-8)
        self.cross1b = (self.target.x+8, self.target.y+8)
        
        self.cross2a = (self.target.x-8, self.target.y+8)
        self.cross2b = (self.target.x+8, self.target.y-8)
    
    def draw(self, surface):
        super().draw(surface)
        pygame.draw.line(surface, self.color, self.cross1a, self.cross1b, width=2)
        pygame.draw.line(surface, self.color, self.cross2a, self.cross2b, width=2)

class MIRV(Missile):
    def __init__(self, start, target, groups={}, color='red', speed=33, split=False, mirv_func=None):
        super().__init__(start, target.rect.midtop, color, speed, groups)
        self.split = split
        self.target_unit = target
        self.mirv_func = mirv_func

        self.explosion_sound = pygame.mixer.Sound(f'{DIR}/assets/explosion2.wav')
        self.explosion_sound.set_volume(0.20)

    def kill(self):
        self.alive = False
        surf = pygame.display.get_surface()
        self.explosion_group.add(Explosion(self.pos, hit_color=surf.get_at((0,0))))
        
    def update(self):
        super().update()
        if self.split and self.pos.y > 200 and self.alive:
            self.alive = False
            self.mirv_func(self.pos)

        elif self.pos == self.target:
            self.target_unit.kill()

class Explosion:
    def __init__(self, pos, collision_group=[], hit_color=None):
        self.alive = True
        self.pos = pos
        self.collision_group = collision_group
        
        self.surface = pygame.Surface((80,80)).convert_alpha()
        self.rect = self.surface.get_rect()
        if hit_color:
            self.surface.set_colorkey(hit_color)
        
        self.frame_idx = 0
        self.radius = 6
        self.growth_speed = 30

        self.hit_color = hit_color
        self.colors = settings.EXPLOSION_COLORS.copy()
        random.shuffle(self.colors)
        self.color = self.colors[int(self.frame_idx)]

    def update(self):
        self.frame_idx += 0.250 # 0.125 | controls speed of animation
        if self.frame_idx >= len(self.colors):
            self.frame_idx = 0

        self.color = self.colors[int(self.frame_idx)]
        self.radius += self.growth_speed * 1/60

        for member in self.collision_group:
            if self.pos.distance_to(member.pos) <= self.radius:
                member.kill()
                post_scoreup(member)
                       
        if self.radius > 40:
            self.growth_speed *= -1
            if self.hit_color:
                self.alive = False
                
        elif self.radius <= 1:
            self.alive = False

    def draw(self, surface):
        self.surface.fill((0,0,0,0))
        pygame.draw.circle(self.surface, self.color,  self.rect.center, self.radius)   
        if self.hit_color:
            pos = (self.rect.centerx+5, self.rect.centery+9)
            pygame.draw.circle(self.surface, self.hit_color, pos, self.radius-2)

        surface.blit(self.surface, (self.pos.x-40, self.pos.y-40))
        
# eof
