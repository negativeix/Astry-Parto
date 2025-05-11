import pygame
import random
# ========== Asteroid Class ==========
class Asteroid:
    def __init__(self, position):
        self.position = list(position)
        self.image = pygame.image.load("assets/asteroid.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=self.position)
        self.contains_powerup = random.choice(
            ['spread', 'laser', 'reverse', 'shield', None
             ])  # 80% chance for powerup

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def check_collision(self, other_rect):
        return self.rect.colliderect(other_rect)