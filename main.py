import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
FPS = 60

# Paths for assets (update these with your actual file paths)
ASSET_PATHS = {
    "BACKGROUND": r"C:\Users\sd876\OneDrive\Desktop\The-Space-War\Background.png",
    "PLAYER": r"C:\Users\sd876\OneDrive\Desktop\The-Space-War\Player Ship.png",
    "ENEMY": r"C:\Users\sd876\OneDrive\Desktop\The-Space-War\Enemy Ship.png",
    "BULLET": r"C:\Users\sd876\OneDrive\Desktop\The-Space-War\player Bullet.png",
    "ENEMY_BULLET": r"C:\Users\sd876\OneDrive\Desktop\The-Space-War\Enemy Bullet.png",
    "GAME_OVER": r"C:\Users\sd876\OneDrive\Desktop\The-Space-War\Game Over.png",
    "EXPLOSION": r"C:\Users\sd876\OneDrive\Desktop\The-Space-War\Explosion.png"
}

# Sound Paths
SOUND_PATHS = {
    "LASER": r"C:\Users\sd876\OneDrive\Desktop\The-Space-War\laser-shot-ingame-230500.mp3",
    "EXPLOSION": r"C:\Users\sd876\OneDrive\Desktop\The-Space-War\medium-explosion-40472.mp3"
}

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Space Shooter Game")

# Load assets with enhanced error handling
def load_asset(path, size=None, convert_alpha=True):
    try:
        # Verify file exists
        if not os.path.exists(path):
            raise FileNotFoundError(f"Asset file not found: {path}")
        
        # Load the image
        asset = pygame.image.load(path)
        
        # Resize if size is provided
        if size:
            asset = pygame.transform.scale(asset, size)
        
        # Convert alpha for better performance
        return asset.convert_alpha() if convert_alpha else asset
    
    except Exception as e:
        print(f"Error loading asset: {path} | {e}")
        
        # Create a fallback surface
        fallback_surface = pygame.Surface(size or (50, 50))
        fallback_surface.fill((255, 0, 0))  # Red fallback color
        return fallback_surface

# Load sounds with comprehensive error handling
def load_sound(path):
    try:
        # Verify file exists
        if not os.path.exists(path):
            raise FileNotFoundError(f"Sound file not found: {path}")
        
        return pygame.mixer.Sound(path)
    
    except Exception as e:
        print(f"Error loading sound: {path} | {e}")
        
        # Return a silent sound as fallback
        return pygame.mixer.Sound(buffer=bytearray())

# Load game assets
# Increased player ship size to 150x150
background = load_asset(ASSET_PATHS["BACKGROUND"], (WIDTH, HEIGHT))
player_ship = load_asset(ASSET_PATHS["PLAYER"], (150, 150))
enemy_ship = load_asset(ASSET_PATHS["ENEMY"], (50, 50))
bullet_img = load_asset(ASSET_PATHS["BULLET"], (10, 30))
enemy_bullet_img = load_asset(ASSET_PATHS["ENEMY_BULLET"], (10, 30))
game_over_img = load_asset(ASSET_PATHS["GAME_OVER"], (WIDTH, HEIGHT))
explosion_img = load_asset(ASSET_PATHS["EXPLOSION"], (100, 100))

# Load sound assets
laser_sound = load_sound(SOUND_PATHS["LASER"])
explosion_sound = load_sound(SOUND_PATHS["EXPLOSION"])

# Fonts
font = pygame.font.Font(None, 36)

# Explosion Animation Class
class Explosion:
    def __init__(self, x, y):
        self.images = [explosion_img]  # Single explosion image for now
        self.current_frame = 0
        self.animation_speed = 5  # Controls animation speed
        self.frame_count = 0
        self.rect = pygame.Rect(x - 50, y - 50, 100, 100)
        self.lifetime = 20  # How long the explosion remains on screen

    def update(self):
        self.frame_count += 1
        return self.frame_count >= self.lifetime

    def draw(self, surface):
        surface.blit(self.images[0], self.rect)

# Player class with improved mouse and keyboard controls
class Player:
    def __init__(self):
        self.image = player_ship
        # Adjusted initial position to account for larger ship size
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        # Reduced speed slightly to account for larger ship
        self.speed = 4
        self.last_shot_time = 0
        self.shoot_delay = 250  # Minimum time between shots (in milliseconds)

    def move(self, keys, mouse_pos=None):
        # Keyboard movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        
        # Mouse movement
        if mouse_pos:
            mouse_x, _ = mouse_pos
            # Smoothly move the ship towards the mouse x-position
            target_x = mouse_x - self.rect.width // 2
            self.rect.x += (target_x - self.rect.x) * 0.3

        # Keep player within screen bounds
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self, current_time):
        # Control shooting rate
        if current_time - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = current_time
            # Adjusted bullet spawn point to match larger ship
            return Bullet(self.rect.centerx, self.rect.top + 20, -7)
        return None

    def draw(self):
        screen.blit(self.image, self.rect)

# Enemy class
class Enemy:
    def __init__(self):
        self.image = enemy_ship
        self.rect = self.image.get_rect(topleft=(random.randint(0, WIDTH - 50), random.randint(-100, -40)))
        self.speed = random.uniform(2, 3)
        self.acceleration = random.uniform(0.01, 0.03)
        self.shoot_delay = random.randint(1000, 3000)
        self.last_shot = pygame.time.get_ticks()

    def move(self):
        self.speed += self.acceleration
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.reset()

    def reset(self):
        self.rect.y = random.randint(-100, -40)
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.speed = random.uniform(2, 3)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            return Bullet(self.rect.centerx - 5, self.rect.bottom, 5, is_enemy=True)
        return None

    def draw(self):
        screen.blit(self.image, self.rect)

# Bullet class
class Bullet:
    def __init__(self, x, y, speed, is_enemy=False):
        self.image = enemy_bullet_img if is_enemy else bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.is_enemy = is_enemy

    def move(self):
        self.rect.y += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

# Game Over function
def game_over(score):
    # Display game over screen
    screen.blit(game_over_img, (0, 0))
    
    # Render final score
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    screen.blit(score_text, score_rect)
    
    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()

# Main game loop
def main():
    clock = pygame.time.Clock()
    player = Player()
    enemies = [Enemy() for _ in range(5)]
    player_bullets = []
    enemy_bullets = []
    explosions = []  # New list to manage explosions
    score = 0

    running = True
    while running:
        # Get current time
        current_time = pygame.time.get_ticks()

        # Handle window resizing
        current_size = screen.get_size()
        background_scaled = pygame.transform.scale(background, current_size)
        screen.blit(background_scaled, (0, 0))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Shooting with mouse or keyboard
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                bullet = player.shoot(current_time)
                if bullet:
                    player_bullets.append(bullet)
                    laser_sound.play()

        # Get current state of input
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # Update player movement
        player.move(keys, mouse_pos)

        # Update enemies
        for enemy in enemies:
            enemy.move()
            bullet = enemy.shoot()
            if bullet:
                enemy_bullets.append(bullet)

        # Update bullets
        player_bullets = [bullet for bullet in player_bullets if bullet.rect.bottom > 0]
        enemy_bullets = [bullet for bullet in enemy_bullets if bullet.rect.top < HEIGHT]

        for bullet in player_bullets:
            bullet.move()

        for bullet in enemy_bullets:
            bullet.move()

        # Collision detection and explosions
        for enemy in enemies[:]:
            for bullet in player_bullets[:]:
                if bullet.rect.colliderect(enemy.rect) and not bullet.is_enemy:
                    player_bullets.remove(bullet)
                    enemies.remove(enemy)
                    # Create an explosion at the enemy's location
                    explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                    enemies.append(Enemy())
                    explosion_sound.play()
                    score += 1

        # Update explosions
        explosions = [explosion for explosion in explosions if not explosion.update()]

        # Enemy bullet collision with player
        for bullet in enemy_bullets[:]:
            if bullet.rect.colliderect(player.rect) and bullet.is_enemy:
                enemy_bullets.remove(bullet)
                explosion_sound.play()
                game_over(score)

        # Draw game objects
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for bullet in player_bullets + enemy_bullets:
            bullet.draw()
        
        # Draw explosions
        for explosion in explosions:
            explosion.draw(screen)

        # Draw score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Refresh screen
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()