import pygame
import sys
import math
import random
import time
import os
import json

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound effects

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2

# Game states
STATE_START_SCREEN = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Projectile Dodge Game")
clock = pygame.time.Clock()

# Create sounds directory if it doesn't exist
sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
os.makedirs(sounds_dir, exist_ok=True)

# Load sound files
try:
    # Game over sound
    game_over_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "game_over.wav"))
    # Point gain sound
    point_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "point.wav"))
    # Level up sound
    level_up_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "level_up.wav"))
    # Projectile launch sound
    projectile_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "projectile.wav"))
except Exception as e:
    print(f"Error loading sound files: {e}")
    # Create silent sounds as fallback
    game_over_sound = pygame.mixer.Sound(buffer=bytes([0]))
    point_sound = pygame.mixer.Sound(buffer=bytes([0]))
    level_up_sound = pygame.mixer.Sound(buffer=bytes([0]))
    projectile_sound = pygame.mixer.Sound(buffer=bytes([0]))

# Game variables
player_pos = [SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4]  # Start player away from center
player_size = 50
player_speed = 5
game_state = STATE_START_SCREEN
score = 0
high_score = 0
difficulty_level = 1

# Highscore file
highscore_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.json")

# Projectile variables
projectiles = []
projectile_size = 15
projectile_speed = 4
last_projectile_time = time.time()
base_projectile_interval = 1.0  # Base interval (1 projectile per second)
projectile_interval = base_projectile_interval  # Current interval
max_angle_deviation = 45  # Maximum angle deviation in degrees (±45° = 90° total range)

# Point object variables
point_pos = [0, 0]
point_size = 20
min_distance_from_center = 150  # Minimum distance from center

class Projectile:
    def __init__(self, target_x, target_y):
        self.x = CENTER_X
        self.y = CENTER_Y

        # Calculate direction vector toward player
        dx = target_x - self.x
        dy = target_y - self.y
        
        # Calculate the angle to the player
        base_angle = math.atan2(dy, dx)
        
        # Add random deviation within ±max_angle_deviation degrees
        angle_deviation = math.radians(random.uniform(-max_angle_deviation, max_angle_deviation))
        final_angle = base_angle + angle_deviation
        
        # Calculate new direction vector with the randomized angle
        self.dx = math.cos(final_angle) * projectile_speed
        self.dy = math.sin(final_angle) * projectile_speed

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

def load_high_score():
    """Load high score from file"""
    global high_score
    try:
        if os.path.exists(highscore_file):
            with open(highscore_file, 'r') as f:
                data = json.load(f)
                high_score = data.get('high_score', 0)
    except Exception as e:
        print(f"Error loading high score: {e}")
        high_score = 0

def save_high_score():
    """Save high score to file"""
    try:
        with open(highscore_file, 'w') as f:
            json.dump({'high_score': high_score}, f)
    except Exception as e:
        print(f"Error saving high score: {e}")

def generate_point_position():
    """Generate a random position for the point object away from the center"""
    while True:
        x = random.randint(point_size, SCREEN_WIDTH - point_size)
        y = random.randint(point_size, SCREEN_HEIGHT - point_size)

        # Check distance from center
        dx = x - CENTER_X
        dy = y - CENTER_Y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance >= min_distance_from_center:
            return [x, y]

def update_difficulty():
    """Update difficulty based on score"""
    global projectile_interval, difficulty_level

    new_level = (score // 5) + 1

    if new_level > difficulty_level:
        # Level up - increase difficulty
        difficulty_level = new_level
        projectile_interval = base_projectile_interval / (1 + (difficulty_level - 1) * 0.2)
        level_up_sound.play()
        return True

    return False

def start_game():
    """Start a new game"""
    global player_pos, projectiles, game_state, score, last_projectile_time, point_pos
    global difficulty_level, projectile_interval

    player_pos = [SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4]
    projectiles = []
    game_state = STATE_PLAYING
    score = 0
    difficulty_level = 1
    projectile_interval = base_projectile_interval
    last_projectile_time = time.time()
    point_pos = generate_point_position()

def reset_game():
    """Reset the game state after game over"""
    global game_state, high_score
    
    # Update high score if needed
    if score > high_score:
        high_score = score
        save_high_score()
    
    # Return to start screen
    game_state = STATE_START_SCREEN

def handle_events():
    """Handle user input events"""
    global player_pos, game_state
    
    player_moved = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        # Check for restart on game over
        if game_state == STATE_GAME_OVER and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
    
    # Handle continuous key presses
    keys = pygame.key.get_pressed()
    
    if game_state == STATE_START_SCREEN:
        # Start the game when player moves
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            start_game()
    
    if game_state == STATE_PLAYING:
        if keys[pygame.K_LEFT]:
            player_pos[0] -= player_speed
            player_moved = True
        if keys[pygame.K_RIGHT]:
            player_pos[0] += player_speed
            player_moved = True
        if keys[pygame.K_UP]:
            player_pos[1] -= player_speed
            player_moved = True
        if keys[pygame.K_DOWN]:
            player_pos[1] += player_speed
            player_moved = True
        
        # Keep player on screen
        player_pos[0] = max(0, min(player_pos[0], SCREEN_WIDTH - player_size))
        player_pos[1] = max(0, min(player_pos[1], SCREEN_HEIGHT - player_size))
    
    return True

def check_point_collision():
    """Check if player has collected the point"""
    global score, point_pos

    # Get player center
    player_center_x = player_pos[0] + player_size/2
    player_center_y = player_pos[1] + player_size/2

    # Get point center
    point_center_x = point_pos[0]
    point_center_y = point_pos[1]

    # Calculate distance
    dx = player_center_x - point_center_x
    dy = player_center_y - point_center_y
    distance = math.sqrt(dx*dx + dy*dy)

    # Check collision (using player_size/2 + point_size as collision radius)
    if distance < (player_size/2 + point_size):
        score += 1
        point_pos = generate_point_position()
        point_sound.play()  # Play point sound

        # Check if difficulty should increase
        update_difficulty()
        return True

    return False

def update():
    """Update game state"""
    global projectiles, last_projectile_time, game_state
    
    if game_state != STATE_PLAYING:
        return
    
    # Generate new projectile based on current interval
    current_time = time.time()
    if current_time - last_projectile_time >= projectile_interval:
        # Create a new projectile aimed at the player's current position
        new_projectile = Projectile(player_pos[0] + player_size/2, player_pos[1] + player_size/2)
        projectiles.append(new_projectile)
        last_projectile_time = current_time
        
        # Play projectile launch sound
        projectile_sound.play()

    # Update projectiles and check for collisions
    i = 0
    while i < len(projectiles):
        if projectiles[i].update():
            # Check for collision with player
            if projectiles[i].check_collision(player_pos[0], player_pos[1], player_size):
                game_state = STATE_GAME_OVER
                game_over_sound.play()  # Play game over sound
                
                # Update high score if needed
                global high_score
                if score > high_score:
                    high_score = score
                    save_high_score()
            i += 1
        else:
            # Remove projectile if it's out of bounds
            projectiles.pop(i)

    # Check if player collected a point
    check_point_collision()

def draw_start_screen():
    """Draw the start screen"""
    screen.fill(BLACK)
    
    # Draw title
    font_title = pygame.font.SysFont(None, 72)
    title_text = font_title.render("PROJECTILE DODGE", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
    
    # Draw instructions
    font_instructions = pygame.font.SysFont(None, 36)
    instructions = [
        "Use ARROW KEYS to move",
        "Collect PURPLE points to score",
        "Avoid YELLOW projectiles",
        "Every 5 points increases difficulty",
        "",
        "Move to start the game"
    ]
    
    # Draw player and projectile examples
    pygame.draw.rect(screen, RED, (SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 80, player_size, player_size))
    pygame.draw.circle(screen, YELLOW, (int(SCREEN_WIDTH/2), int(SCREEN_HEIGHT/2 + 100)), projectile_size)
    pygame.draw.circle(screen, PURPLE, (int(SCREEN_WIDTH/2 + 100), int(SCREEN_HEIGHT/2 + 100)), point_size)
    
    # Draw high score
    high_score_text = font_instructions.render(f"High Score: {high_score}", True, WHITE)
    high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 50))
    
    # Render everything
    screen.blit(title_text, title_rect)
    for i, line in enumerate(instructions):
        instruction_text = font_instructions.render(line, True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50 + i * 30))
        screen.blit(instruction_text, instruction_rect)
    
    screen.blit(high_score_text, high_score_rect)

def draw_game():
    """Draw the game screen"""
    # Clear the screen
    screen.fill(BLACK)

    # Draw center point (source of projectiles)
    pygame.draw.circle(screen, GREEN, (CENTER_X, CENTER_Y), 10)

    # Draw point object
    pygame.draw.circle(screen, PURPLE, (point_pos[0], point_pos[1]), point_size)

    # Draw projectiles
    for projectile in projectiles:
        projectile.draw()

    # Draw player (a simple rectangle)
    pygame.draw.rect(screen, RED, (player_pos[0], player_pos[1], player_size, player_size))

    # Draw score, level and high score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}  Level: {difficulty_level}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH/2, 30))
    
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    high_score_rect = high_score_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
    
    screen.blit(score_text, score_rect)
    screen.blit(high_score_text, high_score_rect)

def draw_game_over():
    """Draw the game over screen"""
    # Draw the game in the background
    draw_game()
    
    # Draw semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Black with alpha
    screen.blit(overlay, (0, 0))
    
    # Draw game over message
    font_large = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)
    
    game_over_text = font_large.render("GAME OVER", True, WHITE)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40))
    
    final_score_text = font_small.render(f"Final Score: {score}", True, WHITE)
    final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))
    
    # Show if high score was achieved
    if score == high_score and score > 0:
        new_high_text = font_small.render("NEW HIGH SCORE!", True, YELLOW)
        new_high_rect = new_high_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60))
        screen.blit(new_high_text, new_high_rect)
    
    restart_text = font_small.render("Press 'R' to Return to Start", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100))
    
    screen.blit(game_over_text, game_over_rect)
    screen.blit(final_score_text, final_score_rect)
    screen.blit(restart_text, restart_rect)

def draw():
    """Draw everything to the screen based on game state"""
    if game_state == STATE_START_SCREEN:
        draw_start_screen()
    elif game_state == STATE_PLAYING:
        draw_game()
    elif game_state == STATE_GAME_OVER:
        draw_game_over()
    
    # Update the display
    pygame.display.flip()

def main():
    """Main game loop"""
    global point_pos
    
    # Load high score
    load_high_score()
    
    # Initialize point position
    point_pos = generate_point_position()

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
