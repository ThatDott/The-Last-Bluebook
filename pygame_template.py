import pygame
import sys
import math
import random
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Projectile Dodge Game")
clock = pygame.time.Clock()

# Game variables
player_pos = [SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4]  # Start player away from center
player_size = 50
player_speed = 5
game_over = False

# Projectile variables
projectiles = []
projectile_size = 15
projectile_speed = 4
last_projectile_time = time.time()
projectile_interval = 1.0  # 1 projectile per second

class Projectile:
    def __init__(self, target_x, target_y):
        self.x = CENTER_X
        self.y = CENTER_Y

        # Calculate direction vector toward player
        dx = target_x - self.x
        dy = target_y - self.y
        distance = max(1, math.sqrt(dx*dx + dy*dy))  # Avoid division by zero

        # Normalize the direction vector
        self.dx = (dx / distance) * projectile_speed
        self.dy = (dy / distance) * projectile_speed

    def update(self):
        self.x += self.dx
        self.y += self.dy

        # Check if projectile is out of bounds
        if (self.x < -projectile_size or self.x > SCREEN_WIDTH + projectile_size or
            self.y < -projectile_size or self.y > SCREEN_HEIGHT + projectile_size):
            return False  # Remove this projectile
        return True

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), projectile_size)

    def check_collision(self, player_x, player_y, player_size):
        # Simple collision detection using distance between centers
        dx = self.x - (player_x + player_size/2)
        dy = self.y - (player_y + player_size/2)
        distance = math.sqrt(dx*dx + dy*dy)

        # If the distance is less than the sum of radii, collision occurred
        # Using player_size/2 as an approximation for player's radius
        return distance < (projectile_size + player_size/2)

def handle_events():
    """Handle user input events"""
    global player_pos

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

    if game_over:
        return True

    # Handle continuous key presses
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT]:
        player_pos[0] += player_speed
    if keys[pygame.K_UP]:
        player_pos[1] -= player_speed
    if keys[pygame.K_DOWN]:
        player_pos[1] += player_speed

    # Keep player on screen
    player_pos[0] = max(0, min(player_pos[0], SCREEN_WIDTH - player_size))
    player_pos[1] = max(0, min(player_pos[1], SCREEN_HEIGHT - player_size))

    return True

def update():
    """Update game state"""
    global projectiles, last_projectile_time, game_over

    if game_over:
        return

    # Generate new projectile every second
    current_time = time.time()
    if current_time - last_projectile_time >= projectile_interval:
        # Create a new projectile aimed at the player's current position
        new_projectile = Projectile(player_pos[0] + player_size/2, player_pos[1] + player_size/2)
        projectiles.append(new_projectile)
        last_projectile_time = current_time

    # Update projectiles and check for collisions
    i = 0
    while i < len(projectiles):
        if projectiles[i].update():
            # Check for collision with player
            if projectiles[i].check_collision(player_pos[0], player_pos[1], player_size):
                game_over = True
                print("Game Over! You were hit by a projectile.")
            i += 1
        else:
            # Remove projectile if it's out of bounds
            projectiles.pop(i)

def draw():
    """Draw everything to the screen"""
    # Clear the screen
    screen.fill(BLACK)

    # Draw center point (source of projectiles)
    pygame.draw.circle(screen, GREEN, (CENTER_X, CENTER_Y), 10)

    # Draw projectiles
    for projectile in projectiles:
        projectile.draw()

    # Draw player (a simple rectangle)
    pygame.draw.rect(screen, RED, (player_pos[0], player_pos[1], player_size, player_size))

    # Draw game over message
    if game_over:
        font = pygame.font.SysFont(None, 72)
        text = font.render("GAME OVER", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(text, text_rect)

    # Update the display
    pygame.display.flip()

def main():
    """Main game loop"""
    running = True

    while running:
        # Handle events
        running = handle_events()

        # Update game state
        update()

        # Draw everything
        draw()

        # Control the game speed
        clock.tick(FPS)

    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
