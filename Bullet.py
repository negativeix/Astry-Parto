import pygame
import math

# ========== Bullet Classes ==========
class Bullet:
    def __init__(self, position, direction):
        self.position = list(position)
        self.direction = direction
        self.speed = 5
        self.size = (6, 6)
        self.rect = pygame.Rect(self.position[0], self.position[1], *self.size)

    def move(self):
        rad = math.radians(self.direction)
        self.position[0] += self.speed * math.cos(rad)
        self.position[1] += self.speed * math.sin(rad)
        self.rect.topleft = self.position

    def check_collision(self, other_rect):
        return self.rect.colliderect(other_rect)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)


class Laser(Bullet):
    def __init__(self, position, direction):
        super().__init__(position, direction)
        self.speed = 12
        self.color = (255, 0, 0)

    def draw(self, screen):
        end_x = self.position[0] + 2000 * math.cos(
            math.radians(self.direction))
        end_y = self.position[1] + 2000 * math.sin(
            math.radians(self.direction))
        pygame.draw.line(screen, self.color, self.position, (end_x, end_y), 4)