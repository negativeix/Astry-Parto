import pygame
import math
import time


class Bot:
    def __init__(self, position, health=2):
        self.position = list(position)
        self.health = health
        self.image = pygame.image.load("assets/ship_red_stroked.png")
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=self.position)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True  # Bot destroyed
        return False


class Bullet:
    def __init__(self, position, direction):
        self.position = list(position)
        self.direction = direction
        self.speed = 5
        self.size = (6, 6)
        self.rect = pygame.Rect(self.position[0], self.position[1],
                                self.size[0],
                                self.size[1])  # Rect for collision


    def move(self):
        radian_angle = math.radians(self.direction)
        self.position[0] += self.speed * math.cos(radian_angle)
        self.position[1] += self.speed * math.sin(radian_angle)
        self.rect.topleft = self.position  # Update rect position

    def check_collision(self, bot):
        """Check if bullet hits bot."""
        return self.rect.colliderect(bot.rect)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)


class Spaceship:
    def __init__(self, position, velocity=(0.5, 0.5), direction=0, health=100):
        self.position = list(position)
        self.velocity = list(velocity)
        self.direction = direction  # Angle in degrees
        self.health = health
        self.bullets = []
        self.bullets_fired = 0
        self.dash_usage = 0
        self.obstacles_destroyed = 0
        self.successful_hits = 0

        # Load spaceship image
        self.image = pygame.image.load("assets/ship_blue_stroked.png")
        self.image = pygame.transform.scale(self.image, (40, 40))

        # Dash tracking
        self.last_a_press = 0
        self.dash_cooldown = 0.3  # Time window to detect double press (300ms)

    def move(self,screen_width,screen_height):
        """Update position based on velocity."""
        radian_angle = math.radians(self.direction)
        self.position[0] += 1.5 * math.cos(
            radian_angle)  # Slow forward movement
        self.position[1] += 1.5 * math.sin(radian_angle)

        self.position[0] = max(0, min(self.position[0], screen_width - 25))
        self.position[1] = max(0, min(self.position[1], screen_height - 25))
    def rotate(self, angle):
        """Rotate the spaceship."""
        self.direction = (self.direction + angle) % 360

    def dash(self):
        """Perform a quick dash forward."""
        self.direction += 75
        radian_angle = math.radians(self.direction)
        self.position[0] += 50 * math.cos(
            radian_angle)  # Dash distance = 40 (spaceship size)
        self.position[1] += 50 * math.sin(radian_angle)
        self.dash_usage += 1

    def shoot(self):
        """Fire a bullet in the current direction."""
        bullet = Bullet(self.position[:], self.direction)
        self.bullets.append(bullet)
        self.bullets_fired += 1

    def draw(self, screen):
        """Render the spaceship and bullets on the screen."""
        rotated_image = pygame.transform.rotate(self.image, -self.direction)
        rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rect.topleft)

        for bullet in self.bullets:
            bullet.draw(screen)


class GameManager:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.player = Spaceship(position=(400, 300))
        self.obstacles = []  # A list of obstacles (not used in this example)
        self.bots = [
            Bot(position=(600, 300)),Bot(position=(900,600))]  # Add a bot at position (600, 300)
        self.time_played = 0.0

        # Load background image
        self.background = pygame.image.load("assets/background-black.png")
        self.background = pygame.transform.scale(self.background, (
        1024, 768))  # Set background size

    def update(self):
        """Update game logic."""
        self.player.move(1024, 768)
        for bullet in self.player.bullets:
            bullet.move()
            for bot in self.bots:
                if bullet.check_collision(bot):
                    if bot.take_damage(
                            1):  # Deal 10 damage and check if bot is destroyed
                        self.bots.remove(bot)  # Remove bot if destroyed
                    self.player.bullets.remove(
                        bullet)  # Remove bullet after collision
                    self.score += 10  # Add score for destroying the bot
                    break  # Exit the loop after the first collision

        self.time_played += 1 / 60  # Assuming 60 FPS

    def check_collisions(self):
        """Check for collisions between spaceship, bullets, and obstacles."""
        pass

    def end_game(self):
        """Handle game over logic."""
        print("Game Over! Final Score:", self.score)


# Pygame setup
pygame.init()
screen = pygame.display.set_mode((1024, 768))  # Set larger screen size
clock = pygame.time.Clock()

game_manager = GameManager()

going = True
while going:
    screen.fill((0, 0, 0))

    # Draw the background image
    screen.blit(game_manager.background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            going = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                current_time = time.time()
                if current_time - game_manager.player.last_a_press < game_manager.player.dash_cooldown:
                    game_manager.player.dash()
                game_manager.player.last_a_press = current_time
            elif event.key == pygame.K_d:
                game_manager.player.shoot()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        game_manager.player.rotate(5)

    game_manager.update()
    game_manager.player.draw(screen)

    # Draw all bots
    for bot in game_manager.bots:
        bot.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit( )