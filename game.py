import pygame
import math
import time


class Bullet:
    def __init__(self, position, direction):
        self.position = list(position)
        self.direction = direction
        self.speed = 5
        self.size = (6, 6)
        self.rect = pygame.Rect(self.position[0], self.position[1],
                                self.size[0], self.size[1])

    def move(self):
        radian_angle = math.radians(self.direction)
        self.position[0] += self.speed * math.cos(radian_angle)
        self.position[1] += self.speed * math.sin(radian_angle)
        self.rect.topleft = self.position

    def check_collision(self, bot):
        return self.rect.colliderect(bot.rect)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)


class Spaceship:
    def __init__(self, position, velocity=(0.5, 0.5), direction=0, health=2):
        self.position = list(position)
        self.velocity = list(velocity)
        self.direction = direction
        self.health = health
        self.bullets = []
        self.max_bullets = 3
        self.last_shot_time = 0
        self.reload_time = 1

        self.image = pygame.image.load("assets/ship_blue_stroked.png")
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=self.position)

        self.last_a_press = 0
        self.dash_cooldown = 0.3

    def move(self, screen_width, screen_height):
        radian_angle = math.radians(self.direction)
        self.position[0] += 1.5 * math.cos(radian_angle)
        self.position[1] += 1.5 * math.sin(radian_angle)
        self.position[0] = max(20, min(self.position[0], screen_width - 20))
        self.position[1] = max(20, min(self.position[1], screen_height - 20))
        self.rect.center = self.position

    def rotate(self, angle):
        self.direction = (self.direction + angle) % 360

    def dash(self):
        radian_angle = math.radians(self.direction)
        self.position[0] += 50 * math.cos(radian_angle)
        self.position[1] += 50 * math.sin(radian_angle)
        self.position[0] = max(20, min(self.position[0], 1024 - 20))
        self.position[1] = max(20, min(self.position[1], 768 - 20))
        self.rect.center = self.position

    def shoot(self):
        bullet = Bullet(self.position[:], self.direction)
        self.bullets.append(bullet)
        self.last_shot_time = time.time()

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.direction)
        rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rect.topleft)
        for bullet in self.bullets:
            bullet.draw(screen)


class Bot(Spaceship):
    def __init__(self, position):
        super().__init__(position)
        self.image = pygame.image.load("assets/ship_red_stroked.png")
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=self.position)


class GameManager:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.players = [Spaceship(position=(400, 300))]
        self.bots = [Bot(position=(600, 300)), Bot(position=(900, 600))]
        self.time_played = 0.0

        self.background = pygame.image.load("assets/background-black.png")
        self.background = pygame.transform.scale(self.background, (1024, 768))

    def get_camera_view(self):
        all_positions = [p.position for p in self.players + self.bots if
                         p.health > 0]
        if not all_positions:
            return (512, 384), 1
        min_x = min(pos[0] for pos in all_positions)
        max_x = max(pos[0] for pos in all_positions)
        min_y = min(pos[1] for pos in all_positions)
        max_y = max(pos[1] for pos in all_positions)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        width = max_x - min_x + 200
        height = max_y - min_y + 200
        zoom = min(1024 / width, 768 / height, 1.5)
        return (center_x, center_y), zoom

    def update(self):
        for player in self.players:
            player.move(1024, 768)
            for bullet in player.bullets[:]:
                bullet.move()
                for bot in self.bots[:]:
                    if bullet.check_collision(bot):
                        if bot.take_damage(10):
                            self.bots.remove(bot)
                        player.bullets.remove(bullet)
                        self.score += 10
                        break
            player.bullets = [b for b in player.bullets if
                              0 <= b.position[0] <= 1024 and 0 <= b.position[
                                  1] <= 768]
        for bot in self.bots:
            bot.move(1024, 768)

        self.time_played += 1 / 60


pygame.init()
screen = pygame.display.set_mode((1024, 768))
clock = pygame.time.Clock()

game_manager = GameManager()

going = True
while going:
    screen.fill((0, 0, 0))
    screen.blit(game_manager.background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            going = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                current_time = time.time()
                if current_time - game_manager.players[0].last_a_press < \
                        game_manager.players[0].dash_cooldown:
                    game_manager.players[0].dash()
                game_manager.players[0].last_a_press = current_time
            elif event.key == pygame.K_d:
                game_manager.players[0].shoot()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        game_manager.players[0].rotate(5)

    game_manager.update()

    for player in game_manager.players:
        if player.health > 0:
            player.draw(screen)

    for bot in game_manager.bots:
        if bot.health > 0:
            bot.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
