import pygame
# ========== PowerUp Class ==========
class PowerUp:
    images = {
        'spread': pygame.image.load('assets/spread.png'),
        'laser': pygame.image.load('assets/laser.png'),
        'reverse': pygame.image.load('assets/reverse.png'),
        'shield': pygame.image.load('assets/shield.png')
    }

    def __init__(self, position, power_type):
        self.position = list(position)
        self.type = power_type
        self.image = pygame.transform.scale(
            self.images.get(self.type, self.images['spread']), (50, 50))
        self.rect = self.image.get_rect(topleft=self.position)

    def draw(self, screen):
        screen.blit(self.image, self.rect)