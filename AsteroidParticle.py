import pygame
import math
import random
class AsteroidParticle:

    def __init__(self):
        margin = 50
        WIDTH = 1024
        HEIGHT = 769
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.x = random.uniform(0, WIDTH)
            self.y = -margin
        elif side == 'bottom':
            self.x = random.uniform(0, WIDTH)
            self.y = HEIGHT + margin
        elif side == 'left':
            self.x = -margin
            self.y = random.uniform(0, HEIGHT)
        else:  # right
            self.x = WIDTH + margin
            self.y = random.uniform(0, HEIGHT)

        angle = math.atan2(HEIGHT / 2 - self.y,
                           WIDTH / 2 - self.x) + random.uniform(-0.5, 0.5)
        speed = random.uniform(0.5, 1.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.size = random.randint(5, 12)
        self.color = (137, 137, 137)

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)),
                           self.size)

    def rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size,
                           self.size * 2, self.size * 2)