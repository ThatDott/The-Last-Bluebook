import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Template")
clock = pygame.time.Clock()

# Game variables
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_size = 50
player_speed = 5

def handle_events():
    """Handle user input events"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

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
    pass

def draw():
    """Draw everything to the screen"""
    # Clear the screen
    screen.fill(BLACK)

    # Draw player (a simple rectangle)
    pygame.draw.rect(screen, RED, (player_pos[0], player_pos[1], player_size, player_size))

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
