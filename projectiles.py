from typing import Callable, Tuple
import math
import pygame
from pygame import Vector2

# ai = (on_start, on_update, on_entity_hit)
class AI:
    ON_START = 0
    ON_UPDATE = 1
    ON_ENT_HIT = 2

def None_func(proj, env):
    pass

def ellipse_draw(proj, surf):
    pygame.draw.ellipse(surf, proj.color, proj.hitbox)

def none_ai():
    return None_func, None_func, None_func

def rotating_and_expanding(center, expanding_speed, rotation_speed):  # rotation speed in degrees
    def on_start(proj, env):
        proj.center = center

    def on_update(proj, env):
        vec = proj.pos
        vec -= proj.center
        vec.rotate_ip(rotation_speed)
        vec += (vec + pygame.Vector2(0.001, 0)).normalize() * expanding_speed
        proj.pos = vec + proj.center
        proj.center += proj.vel

    return on_start, on_update

class Environment:
    def __init__(self, width, height, gravity=pygame.Vector2(0, 0), projectile_limit=-1, dynamic=False):
        self.rect = pygame.Rect(0, 0, width, height)
        self.gravity = gravity
        self.entities = {}
        self.projectiles = {}
        self.dynamic = dynamic
        self.projectile_limit = projectile_limit

    def add_entity(self, ent):
        ent.ai[AI.ON_START](ent, self)
        self.entities[len(self.entities)] = ent

    def add_projectile(self, proj):
        proj_id = len(self.projectiles)
        if proj_id < self.projectile_limit or self.projectile_limit == -1:
            proj.ai[AI.ON_START](proj, self)
            self.projectiles[proj_id] = proj

    def draw_projectiles(self, surface):
        proj_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for proj in self.projectiles.values():
            proj.draw(proj_surface)
        surface.blit(proj_surface, (0, 0))

    def draw_entities(self, surface):
        ent_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for ent in self.entities.values():
            ent.draw(ent_surface)
        surface.blit(ent_surface, (0, 0))

    def update_projectiles(self):
        for proj_id, proj in self.projectiles.copy().items():
            if not self.rect.colliderect(proj.hitbox) and not self.dynamic:
                del self.projectiles[proj_id]
                continue
            for ent in self.entities.values():
                if ent.hitbox.colliderect(proj.hitbox):
                    proj.ai[AI.ON_ENT_HIT](proj, ent)
            proj.update(self)
            proj.vel += self.gravity

    def update_entities(self):
        for ent in self.entities.values():
            ent.update(self)

    def update(self):
        self.update_projectiles()
        self.update_entities()

    def draw(self, surface):
        self.draw_projectiles(surface)
        self.draw_entities(surface)

    def update_and_draw(self, surface):
        self.update()
        self.draw(surface)


class Entity:  # Projectiles are entites
    def __init__(self, x, y, width, height, ai, draw_func, damage=0, mass=0, color=(255, 255, 255)):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.jer = Vector2(0, 0)
        self.mass = mass
        self.color = color
        # self.id = env.get_free_proj_id
        # self.env = env
        self.ai = ai
        self.size = (width, height)
        self.damage = damage
        self.draw_func = draw_func

    @property
    def hitbox(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.width, self.height)

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    def update(self, envir):
        self.ai[AI.ON_UPDATE](self, envir)
        self.pos += self.vel
        self.vel += self.acc
        self.acc += self.jer

    def draw(self, surface):
        self.draw_func(self, surface)


if __name__ == "__main__":
    FPS = 60
    SCRW = 640
    SCRH= 480
    BCKGR = (0, 0, 0)

    pygame.init()
    sc = pygame.display.set_mode((SCRW, SCRH))
    clk = pygame.time.Clock()
    env = Environment(SCRW, SCRH, dynamic=True)
    # for angle in range(0, 360 + 1, 10):
    #     cx, cy = SCRW / 2, SCRH / 2
    #     projx, projy = cx + math.cos(math.radians(angle)) * 2, cy + math.sin(math.radians(angle)) * 2
    #     proj = Entity(projx, projy, 10, 10, (None_func, rotating_and_expanding(pygame.Vector2(cx, cy), 1, 1), None_func), ellipse_draw)
    #     env.add_projectile(proj)
    cx, cy = SCRW / 2, SCRH / 2
    proj = Entity(cx, cy, 10, 10, (*rotating_and_expanding(pygame.Vector2(cx, cy), .3, 360 / 10 + 1.2), None_func), ellipse_draw)
    env.add_projectile(proj)
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                exit()
        sc.fill(BCKGR)
        env.update_and_draw(sc)
        pygame.display.update()
        clk.tick(FPS)