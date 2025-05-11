import pygame
import math
import time
import random
from SmokeParticle import SmokeParticle
from Asteroid import  Asteroid
from AsteroidParticle import AsteroidParticle
from Bullet import Bullet,Laser
from PowerUp import PowerUp

import csv
import os

def save_game_data_to_csv(game_manager):
    filename = "game_data.csv"

    file_exists = os.path.isfile(filename)

    data = {
        'Player Hit': game_manager.player_hit,
        'Total Bullets Fired': game_manager.total_shoot,
        'Power-ups Collected': game_manager.power_coll,
        'Obstacles Destroyed': game_manager.obstacle_destroy,
        'Dash Usage': game_manager.dash_usage,
        'Time Played': game_manager.time_played
    }

    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

    print(f"Game data saved to {filename}")

# ========== Spaceship and Bot Classes ==========
class Spaceship:
    def __init__(self, position):
        self.position = list(position)
        self.direction = 0
        self.health = 1
        self.bullets = []
        self.image = pygame.image.load("assets/ship_blue_stroked.png")
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=self.position)
        # การเคลื่อนที่/หมุน
        self.base_speed = 2  # ลดความเร็วพื้นฐานลง
        self.rotation_step = 5
        self.normal_speed = self.base_speed
        self.speed_boost_until = 0

        # อื่น ๆ
        self.last_a_press = 0
        self.dash_cooldown = 1.5
        self.last_dash_time = 0
        self.power_shots_remaining = 0
        self.power_type = None
        self.rotation_direction = 1
        self.max_ammo = 3
        self.ammo = self.max_ammo
        self.last_shot_time = 0
        self.shield = True
        self.dash_speed = 50
        self.dash_rotated = False

    def dash(self):
        now = time.time()
        if now - self.last_dash_time < self.dash_cooldown:
            return
        rad = math.radians(self.direction) + 45
        self.direction += 45
        self.position[0] += self.dash_speed * math.cos(rad)
        self.position[1] += self.dash_speed * math.sin(rad)
        self.position[0] = max(20, min(self.position[0], 1024 - 20))
        self.position[1] = max(20, min(self.position[1], 768 - 20))
        self.rect.center = self.position
        self.last_dash_time = now
        self.speed_boost_until = now + 1

        back_angle = (self.direction + 180) % 360
        rad_back = math.radians(back_angle)
        perp_angle = (self.direction + 90) % 360
        rad_perp = math.radians(perp_angle)

        base_x = self.position[0] + 30 * math.cos(rad_back)
        base_y = self.position[1] + 30 * math.sin(rad_back)

        offsets = [-6, 0, 6]
        for offset in offsets:
            x = base_x + offset * math.cos(rad_perp)
            y = base_y + offset * math.sin(rad_perp)
            GameManager.instance().smoke_particles.append(
                SmokeParticle((x, y), color=(255, random.randint(50, 100), 0),
                              radius=random.randint(3, 6))
            )

        return True  #dashed

    def move(self, screen_width, screen_height):
        now = time.time()
        current_speed = self.base_speed * 1.1 if now < self.speed_boost_until else self.base_speed

        rad = math.radians(self.direction)
        dx = current_speed * math.cos(rad)
        dy = current_speed * math.sin(rad)

        new_position = [self.position[0] + dx, self.position[1] + dy]
        new_rect = self.rect.copy()
        new_rect.center = new_position

        collided = False

        # collide asteroids
        for asteroid in GameManager.instance().asteroids:
            if new_rect.colliderect(asteroid.rect):
                self.direction = (self.direction + 180) % 360
                GameManager.instance().asteroids.remove(asteroid)
                collided = True
                GameManager.instance().obstacle_destroy += 1
                break

        # collide bots
        if not collided:
            for other in GameManager.instance().players + GameManager.instance().bots:
                if other != self and new_rect.colliderect(other.rect):
                    self.direction = (self.direction + 180) % 360
                    other.direction = (other.direction + 180) % 360
                    collided = True
                    break

        # not chon
        if not collided:
            self.position = new_position
            self.position[0] = max(20,
                                   min(self.position[0], screen_width - 20))
            self.position[1] = max(20,
                                   min(self.position[1], screen_height - 20))
            self.rect.center = self.position

            if self.is_out_of_bounds():
                self.rotate_continuously()

    def update_rect(self):
        self.rect.topleft = (
            self.position[0] - 20, self.position[1] - 20)

    def is_out_of_bounds(self):
        # Check if bot is near the screen boundary
        return self.position[0] <= 20 or self.position[0] >= 1024 - 20 or \
            self.position[1] <= 20 or self.position[1] >= 768 - 20

    def rotate(self, angle):
        self.direction = (
                                     self.direction + angle * self.rotation_direction) % 360

    def shoot(self):
        if self.ammo > 0:
            if self.power_type == 'laser':
                self.bullets.append(Laser(self.position[:], self.direction))
                self.power_shots_remaining -= 1
                if self.power_shots_remaining <= 0:
                    self.power_type = None
            elif self.power_type == 'spread':
                angles = [self.direction - 15, self.direction,
                          self.direction + 15]
                for ang in angles:
                    self.bullets.append(Bullet(self.position[:], ang))
                self.power_shots_remaining -= 1
                if self.power_shots_remaining <= 0:
                    self.power_type = None
            else:
                self.bullets.append(Bullet(self.position[:], self.direction))
            self.ammo -= 1
            self.last_shot_time = time.time()

    def refill_ammo(self):
        if time.time() - self.last_shot_time >= 1 and self.ammo < self.max_ammo:
            self.ammo += 1
            self.last_shot_time = time.time()

    def take_damage(self, damage):
        if self.shield:
            self.shield = False
            return False
        self.health -= damage
        return self.health <= 0

    def collect_powerup(self, power_type):
        if power_type == 'reverse':
            for ship in GameManager.instance().players + GameManager.instance().bots:
                ship.rotation_direction *= -1
        elif power_type == 'shield':
            self.shield = True
        else:
            self.power_type = power_type
            self.power_shots_remaining = 3 if power_type == 'spread' else 1

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.direction)
        rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rect.topleft)
        if self.shield:
            pygame.draw.circle(screen, (0, 255, 255),
                               (int(self.position[0]), int(self.position[1])),
                               28, 2)
        for bullet in self.bullets:
            bullet.draw(screen)
        back_angle = (self.direction + 180) % 360
        rad_back = math.radians(back_angle)
        base_x = self.position[0] + 30 * math.cos(rad_back)
        base_y = self.position[1] + 30 * math.sin(rad_back)
        perp_angle = (self.direction + 90) % 360
        rad_perp = math.radians(perp_angle)
        spacing = 16
        start_offset = -spacing
        for i in range(self.ammo):
            offset = start_offset + i * spacing
            orb_x = base_x + offset * math.cos(rad_perp)
            orb_y = base_y + offset * math.sin(rad_perp)
            color = (255, 255, 255)
            if self.power_type == 'laser':
                color = (255, 0, 0)
            elif self.power_type == 'spread':
                color = (0, 255, 0)
            pygame.draw.circle(screen, color, (int(orb_x), int(orb_y)), 5)

    def is_direction_valid(self, new_direction):
        rad = math.radians(new_direction)
        dx = math.cos(rad)
        dy = math.sin(rad)

        projected_x = self.position[
                          0] + dx * 40
        projected_y = self.position[
                          1] + dy * 40

        return 20 <= projected_x <= 1024 - 20 and 20 <= projected_y <= 768 - 20

    def rotate_continuously(self):
        self.direction += random.choice(
            [-self.rotation_step, self.rotation_step])
        if not self.is_direction_valid(self.direction):
            self.direction = (self.direction + 180) % 360  # reverse di


class Bot(Spaceship):
    def __init__(self, position):
        super().__init__(position)
        self.image = pygame.transform.scale(
            pygame.image.load("assets/ship_red_stroked.png"), (40, 40))
        self.rect = self.image.get_rect(center=self.position)

        self.shoot_cooldown = 1.5
        self.dash_cooldown = 2.0
        self.last_dash_time = 0
        self.last_shot_time = 0

        self.base_speed = 0.75
        self.rotation_step = 2
        self.mode = "shooting"
        self.power = False

        self.direction = random.randint(0, 360)
        self.target_direction = None
        self.rotation_direction = 1  # 1 = clockwise, -1 = counterclockwise
        self.roaming_until = 0

    def ai_rotate_towards(self, target_pos):
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        target_angle = math.degrees(math.atan2(dy, dx)) % 360
        self.target_direction = target_angle

    def ai_shoot_at(self, target_pos):
        if time.time() - self.last_shot_time < self.shoot_cooldown:
            return
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        angle_to = math.degrees(math.atan2(dy, dx)) % 360
        if abs((angle_to - self.direction + 180) % 360 - 180) < 15:
            self.shoot()

    def ai_dash_decision(self):
        now = time.time()
        if now - self.last_dash_time < self.dash_cooldown:
            return
        for pl in GameManager.instance().players:
            for b in pl.bullets:
                if math.dist(self.position, b.position) < 90:
                    ang = math.atan2(b.position[1] - self.position[1],
                                     b.position[0] - self.position[0])
                    dodge = ang + (
                        math.pi / 2 if random.random() > 0.5 else -math.pi / 2)
                    dodge_deg = math.degrees(dodge) % 360
                    self.target_direction = dodge_deg
                    self.dash()
                    return

    def update_ai(self, players, asteroids):
        self.ai_dash_decision()
        screen_w, screen_h = 1024, 768
        screen_center = (screen_w / 2, screen_h / 2)
        screen_radius = math.hypot(screen_w, screen_h) * 0.3

        player_in_close_range = False
        if players:
            self.target_player = min(players,
                                     key=lambda p: math.dist(self.position,
                                                             p.position))
            player_dist = math.dist(self.position, self.target_player.position)
            player_in_close_range = player_dist < screen_radius

        if player_in_close_range:
            self.ai_rotate_towards(self.target_player.position)
            self.ai_shoot_at(self.target_player.position)
        else:
            if time.time() < self.roaming_until:
                pass  # แค่เดินตรงไป
            else:
                action = random.choice(['rotate', 'shoot'])
                if action == 'rotate':
                    self.random_rotate()
                elif action == 'shoot':
                    self.random_shoot()

        self.update_rotation()
        self.move(screen_w, screen_h)

    def update_rotation(self):
        if self.target_direction is None:
            return

        diff = (self.target_direction - self.direction + 360) % 360

        if diff == 0:
            self.target_direction = None
            return

        self.direction = (
          self.direction + self.rotation_direction * self.rotation_step) % 360

        remaining = (self.target_direction - self.direction + 360) % 360
        if remaining < self.rotation_step or remaining > (
                360 - self.rotation_step):
            self.direction = self.target_direction
            self.target_direction = None

    def move(self, w, h):
        now = time.time()
        current_speed = self.base_speed * 0.85 if now < self.speed_boost_until else self.base_speed
        rad = math.radians(self.direction)
        dx = current_speed * math.cos(rad)
        dy = current_speed * math.sin(rad)
        new_pos = [self.position[0] + dx, self.position[1] + dy]
        new_rect = self.rect.copy()
        new_rect.center = new_pos

        collided = False

        for asteroid in GameManager.instance().asteroids:
            if new_rect.colliderect(asteroid.rect):
                self.direction = (self.direction + 180) % 360
                GameManager.instance().asteroids.remove(asteroid)
                collided = True
                GameManager.instance().obstacle_destroy += 1
                break

        if not collided:
            for other in GameManager.instance().players + GameManager.instance().bots:
                if other != self and new_rect.colliderect(other.rect):
                    self.direction = (self.direction + 180) % 360
                    other.direction = (other.direction + 180) % 360
                    collided = True
                    break

        # ถ้าไม่ชนอะไรเลย -> อัปเดตตำแหน่ง
        if not collided:
            self.position = new_pos
            self.position[0] = max(20, min(self.position[0], w - 20))
            self.position[1] = max(20, min(self.position[1], h - 20))
            self.rect.center = self.position

            if self.is_out_of_bounds():
                self.rotate_continuously()

    def random_rotate(self):
        if self.target_direction is not None:
            return
        delta = random.choice([-15, -5, 5, 15])
        if random.random() < 0.5:
            delta = -delta
        self.target_direction = (self.direction + delta) % 360
        self.roaming_until = time.time() + 1

    def random_shoot(self):
        if random.random() < 0.05:
            self.shoot_bullet()

    def random_dash(self):
        if random.random() < 0.005:
            self.dash()

    def shoot_bullet(self):
        self.shoot()
        self.last_shot_time = time.time()

# ========== GameManager Class ==========
class GameManager:
    _instance = None

    def __init__(self):
        GameManager._instance = self
        self.players = [Spaceship((200, 450))]
        self.bots = [Bot((900, 300)), Bot((900, 900))]
        self.asteroids = []
        self.powerups = []
        self.asteroid_timer = 0
        self.asteroid_spawn_interval = 1.5
        self.background = pygame.image.load("assets/background-black.png")
        self.background = pygame.transform.scale(self.background, (1024, 768))
        self.game_over = False
        self.font = pygame.font.SysFont(None, 36)
        self.asteroid_particles = []
        self.asteroid_particle_timer = 0
        self.smoke_particles = []
        self.result_message = ""
        self.time_started = time.time()  # เวลาเริ่มเกม


        # New statistics
        self.player_hit = 0  # Total hits by player bullets
        self.total_shoot = 0  # Total bullets fired by the player
        self.power_coll = {'laser': 0, 'spread': 0,'reverse' : 0, 'shield': 0}  # Track collected power-ups by type
        self.obstacle_destroy = 0  # Track destroyed asteroids and particles
        self.dash_usage = 0  # Track dash usage by the player
        self.time_played=0
    @staticmethod
    def instance():
        return GameManager._instance

    def update(self):
        if self.game_over:
            return

        # Update bots AI
        for bot in self.bots:
            if hasattr(bot, 'update_ai'):
                bot.update_ai(self.players, self.asteroids)

            bot.move(1024, 768)  # Make sure move is called for each bot

        for player in self.players[:]:
            if player.health <= 0:
                self.players.remove(player)
                continue

            player.move(1024, 768)
            player.refill_ammo()

            # Prevent player overlapping with bots
            for bot in self.bots:
                if player.rect.colliderect(bot.rect):
                    dx = player.rect.centerx - bot.rect.centerx
                    dy = player.rect.centery - bot.rect.centery
                    distance = max((dx ** 2 + dy ** 2) ** 0.5, 1)
                    offset = 5
                    player.position[0] += (dx / distance) * offset
                    player.position[1] += (dy / distance) * offset
                    player.update_rect()

            for bullet in player.bullets[:]:

                bullet.move()

                # Check collision with bots
                for bot in self.bots[:]:
                    if bullet.check_collision(bot.rect):
                        if bot.take_damage(1):
                            self.bots.remove(bot)
                        if bullet in player.bullets:
                            player.bullets.remove(bullet)
                        self.player_hit += 1  # Increment player hit count
                        break

                # Check collision with asteroids
                for asteroid in self.asteroids[:]:
                    if bullet.check_collision(asteroid.rect):
                        self.asteroids.remove(asteroid)
                        if bullet in player.bullets:
                            player.bullets.remove(bullet)
                            self.player_hit += 1
                        if asteroid.contains_powerup:
                            self.powerups.append(PowerUp(asteroid.position, asteroid.contains_powerup))
                        self.obstacle_destroy += 1  # Increment destroyed asteroids count
                        break

            # Remove bullets that are out of screen
            player.bullets = [b for b in player.bullets if
                              0 <= b.position[0] <= 1024 and 0 <= b.position[1] <= 768]

        # Update bots
        for i, bot in enumerate(self.bots):
            bot.move(1024, 768)
            bot.refill_ammo()
            for bullet in bot.bullets[:]:
                bullet.move()

                for j, other_bot in enumerate(self.bots):
                    if i != j and bot.rect.colliderect(other_bot.rect):
                        dx = bot.rect.centerx - other_bot.rect.centerx
                        dy = bot.rect.centery - other_bot.rect.centery
                        distance = max((dx ** 2 + dy ** 2) ** 0.5, 1)
                        offset = 5
                        bot.position[0] += (dx / distance) * offset
                        bot.position[1] += (dy / distance) * offset
                        bot.update_rect()

                # Check collision with players
                for player in self.players[:]:
                    if bullet.check_collision(player.rect):
                        if player.take_damage(1):
                            self.players.remove(player)
                            continue
                        if bullet in bot.bullets:
                            bot.bullets.remove(bullet)
                        break

                # Check collision with asteroids
                for asteroid in self.asteroids[:]:
                    if bullet.check_collision(asteroid.rect):
                        self.asteroids.remove(asteroid)
                        if bullet in bot.bullets:
                            bot.bullets.remove(bullet)
                        if asteroid.contains_powerup:
                            self.powerups.append(PowerUp(asteroid.position, asteroid.contains_powerup))
                        self.obstacle_destroy += 1  # Increment destroyed asteroids count
                        break

            # Remove bullets that are out of screen
            bot.bullets = [b for b in bot.bullets if
                           0 <= b.position[0] <= 1024 and 0 <= b.position[1] <= 768]

        # Check powerup collection
        for player in self.players:
            for powerup in self.powerups[:]:
                if player.rect.colliderect(powerup.rect):
                    player.collect_powerup(powerup.type)
                    self.powerups.remove(powerup)
                    self.power_coll[powerup.type] += 1  # Increment collected power-up by type

        for bot in self.bots:
            for powerup in self.powerups[:]:
                if bot.rect.colliderect(powerup.rect):
                    bot.collect_powerup(powerup.type)
                    self.powerups.remove(powerup)
                    self.power_coll[powerup.type] += 1

    # Spawn asteroids
        self.asteroid_timer += 1 / 60
        if self.asteroid_timer >= self.asteroid_spawn_interval and len(self.asteroids) < 10:
            for _ in range(10):  # ลองสุ่มไม่เกิน 10 ครั้ง
                x = random.randint(50, 974)
                y = random.randint(50, 678)
                new_asteroid = Asteroid((x, y))
                new_rect = new_asteroid.rect

                # ตรวจสอบว่าไม่ชนกับผู้เล่น บอท หรือ asteroid อื่น
                conflict = False
                for obj in self.players + self.bots + self.asteroids:
                    if new_rect.colliderect(obj.rect):
                        conflict = True
                        break

                if not conflict:
                    self.asteroids.append(new_asteroid)
                    break  # ออกจาก loop ถ้าสร้างได้แล้ว

            self.asteroid_timer = 0

        self.asteroid_particle_timer += 1 / 60
        if self.asteroid_particle_timer >= 1:
            self.asteroid_particles.append(AsteroidParticle())
            self.asteroid_particle_timer = 0

        # Update asteroid    particles
        for particle in self.asteroid_particles[:]:
            particle.update()

            for player in self.players:
                for bullet in player.bullets[:]:
                    if bullet.check_collision(particle.rect()):
                        player.bullets.remove(bullet)
                        self.asteroid_particles.remove(particle)
                        break

            for bot in self.bots:
                for bullet in bot.bullets[:]:
                    if bullet.check_collision(particle.rect()):
                        bot.bullets.remove(bullet)
                        self.asteroid_particles.remove(particle)

                        break

            # Ship collision
            for ship in self.players + self.bots:
                if particle.rect().colliderect(ship.rect):
                    self.asteroid_particles.remove(particle)
                    break

            self.smoke_particles = [p for p in self.smoke_particles if p.update()]

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        for asteroid in self.asteroids:
            asteroid.draw(screen)

        for powerup in self.powerups:
            powerup.draw(screen)

        for player in self.players:
            if player.health > 0:
                player.draw(screen)

        for bot in self.bots:
            if bot.health > 0:
                bot.draw(screen)

        for particle in self.asteroid_particles:
            particle.draw(screen)

        for particle in self.smoke_particles:
            particle.draw(screen)

# ========== Main Game Loop ==========
def main():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Astry Parto")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    def reset_game():
        game_manager = GameManager()
        game_manager.__init__()
        return game_manager

    game_manager = reset_game()
    going = True

    while going:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                going = False
            elif event.type == pygame.KEYDOWN:
                if game_manager.game_over:
                    if event.key == pygame.K_r:
                        game_manager = reset_game()
                    elif event.key == pygame.K_q:
                        going = False
                else:
                    if event.key == pygame.K_a:
                        current_time = time.time()
                        if current_time - game_manager.players[
                            0].last_a_press < game_manager.players[
                            0].dash_cooldown:
                            if game_manager.players[0].dash():
                                game_manager.dash_usage += 1
                        game_manager.players[0].last_a_press = current_time
                    elif event.key == pygame.K_d:
                        game_manager.players[0].shoot()
                        game_manager.total_shoot += 1

        keys = pygame.key.get_pressed()
        if not game_manager.game_over:
            if keys[pygame.K_a]:
                game_manager.players[0].rotate(5)
            elif keys[pygame.K_s]:
                game_manager.players[0].rotate(-5)

        game_manager.update()

        print(len(game_manager.players), len(game_manager.bots))
        if not game_manager.game_over:
            if len(game_manager.players) == 0:
                game_manager.game_over = True
                game_manager.result_message = "Game Over!"
                game_manager.time_played = time.time() - game_manager.time_started
            if len(game_manager.bots) == 0:
                game_manager.game_over = True
                game_manager.result_message = "You Win!"
                game_manager.time_played = time.time() - game_manager.time_started


        game_manager.draw(screen)
        if game_manager.game_over:
            text = font.render(game_manager.result_message, True,
                               (255, 255, 255))
            restart_text = font.render("Press R to Restart or Q to Quit", True,
                                       (200, 200, 200))
            screen.blit(text,
                        (screen.get_width() // 2 - text.get_width() // 2, 300))
            screen.blit(restart_text, (
            screen.get_width() // 2 - restart_text.get_width() // 2, 360))

            print("Game Over! Here are the stats:")
            print(f"Player Hit: {game_manager.player_hit}")
            print(f"Player Total Bullets Fired: {game_manager.total_shoot}")
            print(f"Power-ups Collected: {game_manager.power_coll}")
            print(f"Obstacles Destroyed (Asteroids): {game_manager.obstacle_destroy}")
            print(f"Dash Usage: {game_manager.dash_usage}")
            print(f"Time Played:{game_manager.time_played}")


        pygame.display.flip()
        clock.tick(60)
    save_game_data_to_csv(game_manager)
    pygame.quit()


def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    clock = pygame.time.Clock()

    small_font = pygame.font.SysFont("comicsansms", 30)

    going = True
    while going:
        screen.fill((15, 15, 11))

        title_image = pygame.image.load("assets/title.png").convert_alpha()

        scale_factor = 0.5
        new_width = int(title_image.get_width() * scale_factor)
        new_height = int(title_image.get_height() * scale_factor)
        title_image = pygame.transform.scale(title_image,
                                             (new_width, new_height))

        x = (1024 - new_width) // 2
        y = 0

        screen.blit(title_image, (x, y))

        play_text = small_font.render("Press P to Play", True, (255, 255, 255))
        quit_text = small_font.render("Press Q to Quit", True, (255, 255, 255))

        screen.blit(play_text, ((1024 - play_text.get_width()) // 2, 450))
        screen.blit(quit_text, ((1024 - quit_text.get_width()) // 2, 500))

        howto1 = small_font.render("Press A to Rotate  |  Double Tap A to Dash", True, (200, 200, 200))
        howto2 = small_font.render("Press D to Shoot  (Max 3 bullets, 1s cooldown)", True, (200, 200, 200))

        screen.blit(howto1, ((1024 - howto1.get_width()) // 2, 600))
        screen.blit(howto2, ((1024 - howto2.get_width()) // 2, 640))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    going = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    return

        pygame.display.flip()
        clock.tick(60)

    main()



if __name__ == "__main__":
    main_menu()




