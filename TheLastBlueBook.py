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
YELLOW = (255, 200, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("POV: FINALS EXAM!")
clock = pygame.time.Clock()

# Create directories if they don't exist
sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(sounds_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)

# Load images or use defaults
try:
    # Try to load player image
    player_image_path = os.path.join(images_dir, "player.png")
    if os.path.exists(player_image_path):
        player_image = pygame.image.load(player_image_path).convert()
    else:
        player_image = pygame.Surface((50, 50))
        player_image.fill(RED)
    
    # Try to load generator image
    generator_image_path = os.path.join(images_dir, "generator.png")
    if os.path.exists(generator_image_path):
        generator_image = pygame.image.load(generator_image_path).convert_alpha()
    else:
        generator_image = pygame.Surface((20, 20))
        generator_image.fill(GREEN)
    
    # Try to load projectile images for different grades
    projectile_images = {}
    grade_levels = ["1.00", "1.25", "1.50", "1.75", "2.00", "2.25", "2.50", "2.75", "3.00", "4.00", "5.00"]
    
    # Load all grade-specific projectile images if they exist
    for grade in grade_levels:
        grade_image_path = os.path.join(images_dir, f"projectile_{grade}.png")
        if os.path.exists(grade_image_path):
            projectile_images[grade] = pygame.image.load(grade_image_path).convert_alpha()
    
    # Default projectile image if no grade-specific images are found
    projectile_image_path = os.path.join(images_dir, "projectile.png")
    if os.path.exists(projectile_image_path):
        default_projectile_image = pygame.image.load(projectile_image_path).convert_alpha()
    else:
        default_projectile_image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(default_projectile_image, YELLOW, (15, 15), 15)
    
    # Try to load point image
    point_image_path = os.path.join(images_dir, "point.png")
    if os.path.exists(point_image_path):
        point_image = pygame.image.load(point_image_path).convert_alpha()
    else:
        point_image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(point_image, PURPLE, (20, 20), 20)
        
except Exception as e:
    print(f"Error loading images: {e}")
    # Create default images if loading fails
    player_image = pygame.Surface((50, 50))
    player_image.fill(RED)
    
    generator_image = pygame.Surface((20, 20))
    generator_image.fill(GREEN)
    
    default_projectile_image = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(default_projectile_image, YELLOW, (15, 15), 15)
    
    projectile_images = {}  # Empty dictionary for grade-specific projectiles
    
    point_image = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(point_image, PURPLE, (20, 20), 20)

# Resize images to match the original sizes
player_size = 50
player_image = pygame.transform.scale(player_image, (0.67 * player_size, player_size))

generator_size = 50
generator_image = pygame.transform.scale(generator_image, (generator_size, generator_size))

projectile_size = 15
# Resize all projectile images
if projectile_images:
    for grade in projectile_images:
        projectile_images[grade] = pygame.transform.scale(projectile_images[grade], (projectile_size*2, projectile_size*2*0.4))
default_projectile_image = pygame.transform.scale(default_projectile_image, (projectile_size*2, projectile_size*2))

point_size = 15
point_image = pygame.transform.scale(point_image, (point_size*2, point_size*2))

# Create sound files if they don't exist
try:
    # Game over sounds - just two variants
    game_over_fail_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "game_over_fail.mp3"))  # For 5.00 and 4.00
    game_over_pass_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "game_over_pass.mp3"))  # For 3.00 and better
    
    # Fallback game over sound
    fallback_game_over_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "game_over.wav"))
    
    # Point gain sound
    point_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "point.mp3"))
    # Level up sound
    level_up_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "level_up.mp3"))
    # Projectile launch sound
    projectile_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "projectile.mp3"))
    
    # Background music
    background_music_path = os.path.join(sounds_dir, "background_music.mp3")
    if os.path.exists(background_music_path):
        pygame.mixer.music.load(background_music_path)
        pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
    else:
        print("Background music file not found. Please add it to the sounds directory.")
except Exception as e:
    print(f"Error loading sound files: {e}")
    # Create silent sounds as fallback
    fallback_game_over_sound = pygame.mixer.Sound(buffer=bytes([0]))
    game_over_fail_sound = pygame.mixer.Sound(buffer=bytes([0]))
    game_over_pass_sound = pygame.mixer.Sound(buffer=bytes([0]))
    point_sound = pygame.mixer.Sound(buffer=bytes([0]))
    level_up_sound = pygame.mixer.Sound(buffer=bytes([0]))
    projectile_sound = pygame.mixer.Sound(buffer=bytes([0]))

# Game variables
player_pos = [SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4]  # Start player away from center
player_speed = 5
game_state = STATE_START_SCREEN
score = 0
high_score = 0
difficulty_level = 1

# Score multiplier variables
score_multiplier = 1
max_multiplier = 5
multiplier_timer = 0
multiplier_duration = 5.0  # 5 seconds to collect the next point
last_point_time = 0

# Highscore file
highscore_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.json")

# Projectile variables
projectiles = []
projectile_speed = 4
last_projectile_time = time.time()
base_projectile_interval = 1.0  # Base interval (1 projectile per second)
projectile_interval = base_projectile_interval  # Current interval
max_angle_deviation = 60  # Maximum angle deviation in degrees (±60° = 120° total range)

# Point object variables
point_pos = [0, 0]
min_distance_from_center = 150  # Minimum distance from center

# Particle system variables
particle_colors = {
    1: WHITE,      # 1x multiplier
    2: GREEN,      # 2x multiplier
    3: BLUE,       # 3x multiplier
    4: ORANGE,     # 4x multiplier
    5: PURPLE      # 5x multiplier
}
particles = []
max_particles = 40  # Maximum number of particles to display at once

# Sprite classes
class ScorePopup:
    def __init__(self, x, y, value, color):
        self.x = x
        self.y = y
        self.value = value
        self.color = color
        self.creation_time = time.time()
        self.lifetime = 1.5  # Lifetime in seconds
        self.alpha = 255     # Start fully opaque
        self.scale = 1.0     # Start at normal size
        self.y_offset = 0    # For upward movement
    
    def update(self):
        # Calculate elapsed time
        elapsed = time.time() - self.creation_time
        remaining_life = max(0, 1 - (elapsed / self.lifetime))
        
        # Update alpha (fade out)
        self.alpha = int(255 * remaining_life)
        
        # Update scale (grow slightly then shrink)
        if elapsed < 0.3:
            # Grow to 1.5x in the first 0.3 seconds
            self.scale = 1.0 + (0.5 * (elapsed / 0.3))
        else:
            # Shrink back to 1.0x over the remaining time
            self.scale = 1.5 - (0.5 * ((elapsed - 0.3) / (self.lifetime - 0.3)))
        
        # Move upward
        self.y_offset = -40 * (elapsed / self.lifetime)
        
        # Return True if still alive
        return elapsed < self.lifetime
    
    def draw(self, surface):
        # Create a font with the current scale
        base_size = 28
        font = pygame.font.SysFont(None, int(base_size * self.scale))
        
        # Render the text with the current alpha
        text = f"+{self.value}"
        text_surface = font.render(text, True, self.color)
        
        # Create a surface with per-pixel alpha
        alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        
        # Fill with transparent color
        alpha_surface.fill((0, 0, 0, 0))
        
        # Blit the text onto the alpha surface with the current alpha
        alpha_surface.blit(text_surface, (0, 0))
        alpha_surface.set_alpha(self.alpha)
        
        # Calculate position with offset
        pos_x = self.x - alpha_surface.get_width() // 2
        pos_y = self.y - alpha_surface.get_height() // 2 + self.y_offset
        
        # Draw to the main surface
        surface.blit(alpha_surface, (pos_x, pos_y))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.size = random.randint(1, 3)
        self.color = color
        self.speed_x = random.uniform(-1, 1)
        self.speed_y = random.uniform(-1, 1)
        self.lifetime = random.uniform(0.5, 1.5)  # Lifetime in seconds
        self.creation_time = time.time()
        self.alpha = 255  # Start fully opaque
    
    def update(self):
        # Update position
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Calculate remaining lifetime as a percentage
        elapsed = time.time() - self.creation_time
        remaining_life = max(0, 1 - (elapsed / self.lifetime))
        
        # Fade out as lifetime decreases
        self.alpha = int(255 * remaining_life)
        
        # Return True if particle is still alive
        return elapsed < self.lifetime
    
    def draw(self, surface):
        # Create a surface with per-pixel alpha
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Get color with alpha
        color_with_alpha = (*self.color, self.alpha)
        
        # Draw the particle
        pygame.draw.circle(particle_surface, color_with_alpha, (self.size, self.size), self.size)
        
        # Blit to the main surface
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.last_particle_time = 0
        self.particle_interval = 0.05  # Time between particle spawns in seconds
    
    def update(self, x, y):
        self.rect.topleft = (x, y)
        
        # Generate particles based on multiplier
        if score_multiplier > 1:
            current_time = time.time()
            if current_time - self.last_particle_time >= self.particle_interval:
                self.generate_particles()
                self.last_particle_time = current_time
    
    def generate_particles(self):
        """Generate particles around the player based on current multiplier"""
        global particles
        
        # Get color based on multiplier
        color = particle_colors.get(score_multiplier, WHITE)
        
        # Number of particles to generate increases with multiplier
        num_particles = score_multiplier
        
        # Generate particles around the player
        for _ in range(num_particles):
            # Calculate random position around the player
            offset_x = random.randint(-10, 10) + self.rect.width // 2
            offset_y = random.randint(-10, 10) + self.rect.height // 2
            
            # Create new particle
            new_particle = Particle(
                self.rect.left + offset_x,
                self.rect.top + offset_y,
                color
            )
            
            # Add to particles list, maintaining maximum count
            particles.append(new_particle)
            if len(particles) > max_particles:
                particles.pop(0)  # Remove oldest particle
    
class Generator(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = generator_image
        self.rect = self.image.get_rect()
        self.rect.center = (CENTER_X, CENTER_Y)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, target_x, target_y):
        super().__init__()
        
        # Determine which projectile image to use based on current difficulty level
        self.image = self.get_projectile_image_for_level(difficulty_level)
        self.rect = self.image.get_rect()
        self.rect.center = (CENTER_X, CENTER_Y)
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
    
    def get_projectile_image_for_level(self, level):
        """Get the appropriate projectile image based on the current difficulty level"""
        # Convert level to grade
        percentage = (score / 200) * 100
        
        if percentage >= 95.2:
            grade = "1.00"
        elif percentage >= 90.8:
            grade = "1.25"
        elif percentage >= 86.4:
            grade = "1.50"
        elif percentage >= 82:
            grade = "1.75"
        elif percentage >= 77.6:
            grade = "2.00"
        elif percentage >= 73.2:
            grade = "2.25"
        elif percentage >= 68.8:
            grade = "2.50"
        elif percentage >= 64.4:
            grade = "2.75"
        elif percentage >= 60:
            grade = "3.00"
        elif percentage >= 55:
            grade = "4.00"
        else:
            grade = "5.00"
        
        # Return the appropriate image if it exists, otherwise use default
        if grade in projectile_images:
            return projectile_images[grade]
        return default_projectile_image
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (self.x, self.y)
        
        # Check if projectile is out of bounds
        if (self.x < -projectile_size or self.x > SCREEN_WIDTH + projectile_size or
            self.y < -projectile_size or self.y > SCREEN_HEIGHT + projectile_size):
            return False  # Remove this projectile
        return True
    
    def check_collision(self, player_rect):
        # Use pygame's built-in collision detection
        return self.rect.colliderect(player_rect)

class Point(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = point_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    def update(self, x, y):
        self.rect.center = (x, y)

# Create sprite instances
player = Player(player_pos[0], player_pos[1])
generator = Generator()
point = Point(0, 0)  # Will be positioned later

# Sprite groups
all_sprites = pygame.sprite.Group()
projectile_sprites = pygame.sprite.Group()
all_sprites.add(generator)
all_sprites.add(player)
all_sprites.add(point)

def get_grade_info(score):
    """Get grade and message based on score percentage"""
    percentage = (score / 200) * 100
    
    if percentage > 100:
        grade = "1.00"
        message = "SUMMA-SOBRA NA SA TOTAL! WOWOWOW!"
    elif percentage >= 95.2:
        grade = "1.00"
        message = "HALIMAW! SUMMA CUM LAUDE!"
    elif percentage >= 90.8:
        grade = "1.25"
        message = "FLAT UNO NA UNTA AHGHHDFHFGH"
    elif percentage >= 86.4:
        grade = "1.50"
        message = "Sarap! wan-poynt-payb!"
    elif percentage >= 82:
        grade = "1.75"
        message = "Wow college scholar!"
    elif percentage >= 77.6:
        grade = "2.00"
        message = "Dos por dos. So goods!"
    elif percentage >= 73.2:
        grade = "2.25"
        message = "Hapit na flat dos!"
    elif percentage >= 68.8:
        grade = "2.50"
        message = "Okay lang. Okay nato"
    elif percentage >= 64.4:
        grade = "2.75"
        message = "Yes dili Tres!"
    elif percentage >= 60:
        grade = "3.00"
        message = "Importante Pasar! Amen!"
    elif percentage >= 55:
        grade = "4.00"
        message = "Conditional! Take Removal!"
    else:
        grade = "5.00"
        message = "SINGKO! RETAKE!"
    
    return percentage, grade, message

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
        y = random.randint(point_size + 30, SCREEN_HEIGHT - point_size)

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

def update_multiplier():
    """Update the score multiplier based on time since last point"""
    global score_multiplier, multiplier_timer
    
    if score_multiplier > 1:
        current_time = time.time()
        elapsed = current_time - last_point_time
        
        # Calculate remaining time for multiplier
        multiplier_timer = max(0, multiplier_duration - elapsed)
        
        # Reset multiplier if timer runs out
        if multiplier_timer <= 0:
            score_multiplier = 1

def start_game():
    """Start a new game"""
    global player_pos, projectiles, game_state, score, last_projectile_time, point_pos
    global difficulty_level, projectile_interval, score_multiplier, last_point_time
    global projectile_sprites, particles, score_popups

    player_pos = [SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4]
    player.update(player_pos[0], player_pos[1])
    
    # Clear projectiles, particles, and score popups
    projectiles = []
    particles = []
    score_popups = []
    projectile_sprites.empty()
    
    game_state = STATE_PLAYING
    score = 0
    difficulty_level = 1
    projectile_interval = base_projectile_interval
    last_projectile_time = time.time()
    
    # Generate new point position
    point_pos = generate_point_position()
    point.update(point_pos[0], point_pos[1])
    
    score_multiplier = 1
    last_point_time = time.time()
    
    # Restart background music if it's not playing
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)

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
        
        # Music controls - M key to mute/unmute
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            if pygame.mixer.music.get_volume() > 0:
                pygame.mixer.music.set_volume(0)  # Mute
            else:
                pygame.mixer.music.set_volume(0.5)  # Unmute to 50%
    
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
        
        # Update player sprite position
        player.update(player_pos[0], player_pos[1])
    
    return True

def check_point_collision():
    """Check if player has collected the point"""
    global score, point_pos, score_multiplier, last_point_time, score_popups
    
    # Use sprite collision detection
    if player.rect.colliderect(point.rect):
        current_time = time.time()
        
        # Add score with multiplier (score_multiplier points per collection)
        score += score_multiplier
        
        # Create a score popup at the point's position
        popup_color = particle_colors.get(score_multiplier, WHITE)
        score_popups.append(ScorePopup(point_pos[0], point_pos[1], score_multiplier, popup_color))

        # Check if this point was collected within the multiplier time window
        if current_time - last_point_time < multiplier_duration:
            # Increase multiplier (up to max)
            score_multiplier = min(score_multiplier + 1, max_multiplier)
        else:
            # Reset multiplier if too much time has passed
            score_multiplier = 1
        
        # Update last point time
        last_point_time = current_time
        
        # Generate new point
        point_pos = generate_point_position()
        point.update(point_pos[0], point_pos[1])
        point_sound.play()  # Play point sound
        
        # Check if difficulty should increase
        update_difficulty()
        return True
    
    return False

def update():
    """Update game state"""
    global projectiles, last_projectile_time, game_state, projectile_sprites, particles, score_popups
    
    if game_state != STATE_PLAYING:
        return
    
    # Update multiplier timer
    update_multiplier()
    
    # Update particles
    i = 0
    while i < len(particles):
        if particles[i].update():
            i += 1
        else:
            particles.pop(i)
    
    # Update score popups
    i = 0
    while i < len(score_popups):
        if score_popups[i].update():
            i += 1
        else:
            score_popups.pop(i)
    
    # Generate new projectile based on current interval
    current_time = time.time()
    if current_time - last_projectile_time >= projectile_interval:
        # Create a new projectile aimed at the player's current position
        new_projectile = Projectile(player_pos[0] + player_size/2, player_pos[1] + player_size/2)
        projectiles.append(new_projectile)
        projectile_sprites.add(new_projectile)
        last_projectile_time = current_time
        
        # Play projectile launch sound
        projectile_sound.play()

    # Update projectiles and check for collisions
    i = 0
    while i < len(projectiles):
        if projectiles[i].update():
            # Check for collision with player
            if projectiles[i].check_collision(player.rect):
                game_state = STATE_GAME_OVER
                
                # Play appropriate game over sound based on score/grade
                percentage = (score / 200) * 100
                
                # Just two sound effects - one for failing grades, one for passing grades
                if percentage >= 60:  # 3.00 and better (passing)
                    try:
                        game_over_pass_sound.play()
                    except:
                        fallback_game_over_sound.play()
                else:  # 4.00 and 5.00 (failing or conditional)
                    try:
                        game_over_fail_sound.play()
                    except:
                        fallback_game_over_sound.play()
                
                # Update high score if needed
                global high_score
                if score > high_score:
                    high_score = score
                    save_high_score()
            i += 1
        else:
            # Remove projectile if it's out of bounds
            projectile_sprites.remove(projectiles[i])
            projectiles.pop(i)

    # Check if player collected a point
    check_point_collision()

def draw_start_screen():
    """Draw the start screen"""
    screen.fill(BLACK)
    
    # Draw author
    font_author = pygame.font.SysFont(None, 20)
    author_text = font_author.render("Developed by: ThatDott", True, WHITE)
    author_rect = author_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/6 + 4))
    
    # Draw title
    font_title = pygame.font.SysFont(None, 72)
    title_text = font_title.render("THE LAST BLUEBOOK", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/6 - 30))
    
    # Draw context
    font_context = pygame.font.SysFont(None, 28)
    context_text = [
        "Finals week. Last sem. 200-items exam.",
        "Ikaw ang last bluebook para mosalba sa imong grado!.",
        "Collect correct answers to increase your score.",
        "Dodge the flying grades — from Singko all the way to Uno!",
        "The longer you survive, the higher the grades that chase you.",
        "Reach 60% or more to pass... kung dili, Singko!",
    ]
    
    # Draw instructions
    font_instructions = pygame.font.SysFont(None, 24)
    instructions = [
        "ARROW KEYS: Move your bluebook",
        "Collect CORRECT ANSWERS to increase your score",
        "Avoid flying GRADES – all can end your exam",
        "Every 5 points, the exam gets harder!",
        "Collect answers quickly to boost your multiplier",
        "Press M to mute/unmute the background music"
    ]
    
    # Draw player and projectile examples with labels
    screen.blit(player_image, (SCREEN_WIDTH/2 + 98, SCREEN_HEIGHT/2 + 90))
    screen.blit(point_image, (SCREEN_WIDTH/2 + 215, SCREEN_HEIGHT/2 + 100))
    
    # Use the appropriate projectile image for the example
    example_projectile = default_projectile_image
    if "5.00" in projectile_images:
        example_projectile = projectile_images["5.00"]  # Start with the worst grade
    screen.blit(example_projectile, (SCREEN_WIDTH/2 + 305, SCREEN_HEIGHT/2 + 118))
    
    label_font = pygame.font.SysFont(None, 20)
    textbook_label = label_font.render("YOU", True, WHITE)
    correct_label = label_font.render("COLLECT", True, WHITE)
    wrong_label = label_font.render("AVOID", True, WHITE)
    
    screen.blit(textbook_label, (SCREEN_WIDTH/2 + 100, SCREEN_HEIGHT/2 + 150))
    screen.blit(correct_label, (SCREEN_WIDTH/2 + 200, SCREEN_HEIGHT/2 + 150))
    screen.blit(wrong_label, (SCREEN_WIDTH/2 + 300, SCREEN_HEIGHT/2 + 150))
    
    # Draw high score
    high_score_text = font_instructions.render(f"Best Score: {high_score}", True, WHITE)
    high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 30))
    
    # Draw start instruction
    start_text = font_instructions.render("Move to start the exam!", True, YELLOW)
    start_rect = start_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 60))
    
    # Render everything
    screen.blit(author_text, author_rect)
    screen.blit(title_text, title_rect)
    
    # Render context
    for i, line in enumerate(context_text):
        context_line = font_context.render(line, True, WHITE)
        context_rect = context_line.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4 + i * 30))
        screen.blit(context_line, context_rect)
    
    # Render instructions
    for i, line in enumerate(instructions):
        instruction_text = font_instructions.render(line, True, WHITE)
        instruction_rect = instruction_text.get_rect(left=50, top=SCREEN_HEIGHT/2 + 60 + i * 25)
        screen.blit(instruction_text, instruction_rect)
    
    screen.blit(high_score_text, high_score_rect)
    screen.blit(start_text, start_rect)

def draw_multiplier_bar():
    """Draw the multiplier timer bar and current multiplier"""
    # Get multiplier color based on level
    if score_multiplier == 1:
        multiplier_color = WHITE  # Lowest multiplier (1x)
    elif score_multiplier == 2:
        multiplier_color = GREEN  # 2x multiplier
    elif score_multiplier == 3:
        multiplier_color = BLUE   # 3x multiplier
    elif score_multiplier == 4:
        multiplier_color = ORANGE # 4x multiplier
    else:
        multiplier_color = PURPLE # Highest multiplier (5x)
    
    # Always draw multiplier text with color based on level
    font = pygame.font.SysFont(None, 36)
    multiplier_text = font.render(f"{score_multiplier}x", True, multiplier_color)
    multiplier_rect = multiplier_text.get_rect(topleft=(20, 20))
    screen.blit(multiplier_text, multiplier_rect)
    
    # Draw timer bar background
    bar_width = 150
    bar_height = 15
    bar_x = 60
    bar_y = 30
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
    
    # Draw timer bar fill only if multiplier > 1
    if score_multiplier > 1:
        fill_width = int((multiplier_timer / multiplier_duration) * bar_width)
        if fill_width > 0:
            pygame.draw.rect(screen, multiplier_color, (bar_x, bar_y, fill_width, bar_height))
            
        # Add pulsing effect to the multiplier text when active
        pulse_scale = 1.0 + 0.2 * math.sin(time.time() * 8)  # Pulsing between 0.8 and 1.2 times original size
        pulse_font = pygame.font.SysFont(None, int(36 * pulse_scale))
        pulse_text = pulse_font.render(f"{score_multiplier}x", True, multiplier_color)
        pulse_rect = pulse_text.get_rect(center=multiplier_rect.center)
        screen.blit(pulse_text, pulse_rect)

def draw_game():
    """Draw the game screen"""
    # Clear the screen
    screen.fill(BLACK)
    
    # Draw all particles
    for particle in particles:
        particle.draw(screen)

    # Draw all sprites
    all_sprites.draw(screen)
    projectile_sprites.draw(screen)
    
    # Draw all score popups
    for popup in score_popups:
        popup.draw(screen)

    # Get percentage only (not grade or message during gameplay)
    percentage = (score / 200) * 100
    
    # Draw score, percentage, level and high score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score} ({percentage:.1f}%)  Level: {difficulty_level}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH/2, 30))
    
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    high_score_rect = high_score_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
    
    screen.blit(score_text, score_rect)
    screen.blit(high_score_text, high_score_rect)
    
    # Draw multiplier bar if active
    draw_multiplier_bar()

def draw_game_over():
    """Draw the game over screen"""
    # Draw the game in the background
    draw_game()
    
    # Draw semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Black with alpha
    screen.blit(overlay, (0, 0))
    
    # Get grade information
    percentage, grade, message = get_grade_info(score)
    
    # Draw game over message
    font_large = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)
    
    game_over_text = font_large.render("GAME OVER", True, WHITE)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 80))
    
    final_score_text = font_small.render(f"Final Score: {score} ({percentage:.1f}%)", True, WHITE)
    final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20))
    
    grade_text = font_small.render(f"Grade: {grade}", True, WHITE)
    grade_rect = grade_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 10))
    
    message_text = font_small.render(message, True, YELLOW)
    message_rect = message_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40))
    
    # Show if high score was achieved
    if score == high_score and score > 0:
        new_high_text = font_small.render("NEW HIGH SCORE!", True, YELLOW)
        new_high_rect = new_high_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 70))
        screen.blit(new_high_text, new_high_rect)
    
    restart_text = font_small.render("Press 'R' to Return to Start", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 110))
    
    screen.blit(game_over_text, game_over_rect)
    screen.blit(final_score_text, final_score_rect)
    screen.blit(grade_text, grade_rect)
    screen.blit(message_text, message_rect)
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
    point.update(point_pos[0], point_pos[1])

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
    pygame.mixer.music.stop()  # Stop music before quitting
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
# Particle system variables
particle_colors = {
    1: WHITE,      # 1x multiplier
    2: GREEN,      # 2x multiplier
    3: BLUE,       # 3x multiplier
    4: ORANGE,     # 4x multiplier
    5: PURPLE      # 5x multiplier
}
particles = []
max_particles = 40  # Maximum number of particles to display at once

# Score popup variables
score_popups = []

# Point object variables
point_pos = [0, 0]
min_distance_from_center = 150  # Minimum distance from center
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.last_particle_time = 0
        self.particle_interval = 0.05  # Time between particle spawns in seconds
    
    def update(self, x, y):
        self.rect.topleft = (x, y)
        
        # Generate particles based on multiplier
        if score_multiplier > 1:
            current_time = time.time()
            if current_time - self.last_particle_time >= self.particle_interval:
                self.generate_particles()
                self.last_particle_time = current_time
    
    def generate_particles(self):
        """Generate particles around the player based on current multiplier"""
        global particles
        
        # Get color based on multiplier
        color = particle_colors.get(score_multiplier, WHITE)
        
        # Number of particles to generate increases with multiplier
        num_particles = score_multiplier
        
        # Generate particles around the player
        for _ in range(num_particles):
            # Calculate random position around the player
            offset_x = random.randint(-10, 10) + self.rect.width // 2
            offset_y = random.randint(-10, 10) + self.rect.height // 2
            
            # Create new particle
            new_particle = Particle(
                self.rect.left + offset_x,
                self.rect.top + offset_y,
                color
            )
            
            # Add to particles list, maintaining maximum count
            particles.append(new_particle)
            if len(particles) > max_particles:
                particles.pop(0)  # Remove oldest particle
