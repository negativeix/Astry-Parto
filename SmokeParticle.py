import pygame
import math
import time
import random
class SmokeParticle:
    def __init__(self, position, radius=None, color=None):
        self.position = list(position)
        self.radius = radius if radius is not None else random.randint(6, 10)
        self.alpha = 255
        self.lifetime = 0.4
        self.creation_time = time.time()

        self.surface = pygame.Surface((self.radius * 2, self.radius * 2),
                                      pygame.SRCALPHA)
        self.color = color if color else random.choice([
            (255, 80, 0),  # ส้มแดง
            (255, 120, 40),  # ส้มอ่อน
            (255, 0, 0)  # แดงสด
        ])

    def update(self):
        elapsed = time.time() - self.creation_time
        if elapsed > self.lifetime:
            return False

        self.alpha = max(0, 255 - int((elapsed / self.lifetime) * 255))
        self.surface.fill((0, 0, 0, 0))  # เคลียร์พื้นหลังโปร่งใส

        # วาดวงกลมไอพ่น
        faded_color = (*self.color, self.alpha)
        pygame.draw.circle(self.surface, faded_color,
                           (self.radius, self.radius), self.radius)
        return True

    def draw(self, screen):
        screen.blit(self.surface, (
        self.position[0] - self.radius, self.position[1] - self.radius))