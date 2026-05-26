import pygame
import random
import sys
import math
import os
import json

pygame.init()

# Window configurations
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Pork")
clock = pygame.time.Clock()

# --- CUSTOM OTF FONT CONFIGURATION ---
FONT_FILE = "LowresPixel-Regular.otf" 

try:
    font_large = pygame.font.Font(FONT_FILE, 36)
    font_small = pygame.font.Font(FONT_FILE, 22)
    font_tiny = pygame.font.Font(FONT_FILE, 16)
except:
    font_large = pygame.font.SysFont("Courier New", 36, bold=True)
    font_small = pygame.font.SysFont("Courier New", 22, bold=True)
    font_tiny = pygame.font.SysFont("Courier New", 16, bold=True)

# Image loading
pipe_img = pygame.image.load("pipe.png").convert_alpha()
bg_img = pygame.image.load("bg.png").convert()
saucepan_img = pygame.image.load("pan.png").convert_alpha()
bacon_img = pygame.image.load("bacon.png").convert_alpha()

menu_bg_img = pygame.image.load("bg.png").convert()

# Scale static background and object elements
MENU_BG_SPRITE = pygame.transform.scale(menu_bg_img, (WIDTH, HEIGHT))
BG_SPRITE = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
SAUCEPAN_SPRITE = pygame.transform.scale(saucepan_img, (40, 40))

# Colours
WHITE = (255, 255, 255)
DARK_GRAY = (30, 30, 30)
GOLD = (255, 215, 0)
RED = (200, 50, 50)

# --- LOCAL HIGH SCORE PERSISTENCE LOGIC ---
HIGH_SCORE_FILE = "highscore.txt"

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

def save_high_score(new_high):
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(new_high))
    except:
        pass

# Load startup record
high_score = load_high_score()

# Pig Main Character logic
class PigCharacter:
    def __init__(self):
        self.x = 80  
        self.y = 300
        self.velocity = 0.0
        self.gravity = 0.35  
        self.jump_force = -6.5 
        
        # Power-up variables
        self.is_bacon = False
        self.bacon_timer = 0
        self.invincible_frames = 0  
        
        # Rainbow Trail Array
        self.trail_particles = []
        self.hue_counter = 0.0
        
        # --- UNIVERSAL TRACKING AND PATH RESOLUTION ---
        if getattr(sys, 'frozen', False):
            self.script_dir = os.path.dirname(sys.executable)
        else:
            self.script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
        
        self.universe_save_path = os.path.join(self.script_dir, "porkade_universe.json")
        
        # Safe baseline defaults before loading
        self.porkoins = 0
        self.equipped_skin = "player_pig.png" 
        
        # Load data from the master save file
        self.load_universe_data()
        
        # --- FIXED DYNAMIC PYGAME IMAGE LOADER & FORCE AUTO-SCALE ---
        # Look for the current skin, fallback directly to Bird.png if it's missing
        target_file = self.equipped_skin if os.path.exists(os.path.join(self.script_dir, self.equipped_skin)) else "Bird.png"
        player_image_path = os.path.join(self.script_dir, target_file)
        
        try:
            raw_img = pygame.image.load(player_image_path).convert_alpha()
            
            # AUTO-CROP TRICK: This crops away empty transparent space around the pig automatically!
            image_rect = raw_img.get_bounding_rect()
            cropped_subsurface = raw_img.subsurface(image_rect)
            
            # FORCE LARGE SIZE: Change (65, 65) to something even larger like (80, 80) if you want it huge!
            scaled_img = pygame.transform.scale(cropped_subsurface, (65, 65))
            
            # FLIP DIRECTION: Flip horizontally so it faces right
            self.active_sprite = pygame.transform.flip(scaled_img, True, False)
        except Exception as e:
            print(f"Failed to compile custom sprite configurations: {e}")
            # Extreme emergency baseline block asset if load errors occur
            self.active_sprite = pygame.Surface((65, 65), pygame.SRCALPHA)
            pygame.draw.circle(self.active_sprite, (232, 67, 147), (32, 32), 30)
        
    def update(self, current_speed):
        self.velocity += self.gravity
        self.y += self.velocity
        
        if self.is_bacon:
            self.bacon_timer -= 1
            if self.bacon_timer <= 0:
                self.is_bacon = False  
                
            self.hue_counter = (self.hue_counter + 5) % 360  
            self.trail_particles.append({
                "pos": [self.x, int(self.y)], 
                "hue": self.hue_counter,
                "radius": 16
            })
                
        if self.invincible_frames > 0:
            self.invincible_frames -= 1
            
        for p in self.trail_particles:
            p["pos"][0] -= current_speed  
            p["radius"] -= 0.4            
            
        self.trail_particles = [p for p in self.trail_particles if p["radius"] > 0 and p["pos"][0] > -20]
        
        if self.y > 585: self.y = 585
        if self.y < 15: self.y = 15
        
    def flap(self):
        self.velocity = self.jump_force
        
    def draw_trail(self):
        for p in self.trail_particles:
            if p["radius"] > 0:
                color = pygame.Color(0)
                color.hsva = (p["hue"], 100, 100, 100)
                pygame.draw.circle(screen, color, (int(p["pos"][0]), int(p["pos"][1])), int(p["radius"]))
    
    def draw(self):
        if self.invincible_frames > 0 and (self.invincible_frames // 4) % 2 == 0:
            return  
            
        # Get dimensions dynamically to always maintain true pixel alignment centering
        sprite_w = self.active_sprite.get_width()
        sprite_h = self.active_sprite.get_height()
        offset_x = sprite_w // 2
        offset_y = sprite_h // 2

        if self.is_bacon:
            scaled_bacon = pygame.transform.scale(bacon_img, (sprite_w, sprite_h))
            screen.blit(scaled_bacon, (self.x - offset_x, int(self.y) - offset_y))
        else:
            screen.blit(self.active_sprite, (self.x - offset_x, int(self.y) - offset_y))

    def load_universe_data(self):
        if os.path.exists(self.universe_save_path):
            try:
                with open(self.universe_save_path, "r") as f:
                    data = json.load(f)
                self.porkoins = data.get("porkoins", 0)
                self.equipped_skin = data.get("equipped_skin", "player_pig.png")
            except Exception as e:
                print(f"Error reading master registry file: {e}")

    def save_universe_data(self):
        try:
            data = {}
            if os.path.exists(self.universe_save_path):
                with open(self.universe_save_path, "r") as f:
                    try: data = json.load(f)
                    except Exception: pass

            data["porkoins"] = self.porkoins
            data["equipped_skin"] = self.equipped_skin

            with open(self.universe_save_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to compile save state data packet: {e}")

# Pipe logic
class Pipe:
    def __init__(self, speed, gap):
        self.x = WIDTH
        self.gap = gap
        self.width = 60
        self.top = random.randint(50, 350) 
        self.bottom = self.top + self.gap
        self.passed = False
        self.speed = speed
        
        top_pipe_scaled = pygame.transform.scale(pipe_img, (self.width, self.top))
        self.top_pipe_surface = pygame.transform.flip(top_pipe_scaled, False, True)
        
        bottom_height = HEIGHT - self.bottom
        self.bottom_pipe_surface = pygame.transform.scale(pipe_img, (self.width, bottom_height))
        
    def update(self):
        self.x -= self.speed
        
    def draw(self):
        screen.blit(self.top_pipe_surface, (self.x, 0))
        screen.blit(self.bottom_pipe_surface, (self.x, self.bottom))
        
    def hit(self, pig):
        if pig.invincible_frames > 0:
            return False
            
        if pig.x + 15 > self.x and pig.x - 15 < self.x + self.width:
            if pig.y - 15 < self.top or pig.y + 15 > self.bottom:
                return True
        return False

# Saucepan logic
class Saucepan:
    def __init__(self, speed):
        self.x = WIDTH
        self.y = random.randint(150, 450)  
        self.width = 40
        self.height = 40
        self.collected = False
        self.speed = speed
        
    def update(self):
        self.x -= self.speed  
        
    def draw(self):
        if not self.collected:
            screen.blit(SAUCEPAN_SPRITE, (self.x, self.y))
            
    def check_collision(self, pig):
        if not self.collected:
            if (self.x < pig.x + 23 and self.x + self.width > pig.x - 23 and
                self.y < pig.y + 23 and self.y + self.height > pig.y - 23):
                self.collected = True
                return True
        return False

def reset_game():
    return PigCharacter(), [Pipe(speed=2, gap=160)], 0, False, []

# Game States
STATE_MENU = "menu"
STATE_GAME = "game"
current_state = STATE_MENU

pig, pipes, score, game_over, saucepans = reset_game()
animation_timer = 0

current_level = 1
level_speed = 2
level_gap = 160

# --- MAIN GAME LOOP ---
while True:
    clock.tick(60)
    screen.blit(BG_SPRITE, (0, 0))
    animation_timer += 1
    
    pulse_val = int(197 + 58 * math.sin(animation_timer * 0.1))
    text_color = (pulse_val, pulse_val, pulse_val)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if current_state == STATE_MENU:
                pig, pipes, score, game_over, saucepans = reset_game()
                current_level = 1
                level_speed = 2
                level_gap = 160
                current_state = STATE_GAME
            elif current_state == STATE_GAME:
                if not game_over:
                    pig.flap()
                else: 
                    pig, pipes, score, game_over, saucepans = reset_game()
                    current_state = STATE_MENU

    # --- STATE MACHINE LOGIC ---
    if current_state == STATE_MENU:
        screen.blit(MENU_BG_SPRITE, (0, 0))

        title_shadow = font_large.render("FLAPPY PORK", True, (0, 0, 0))
        shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + 3, HEIGHT // 4 + 43))
        screen.blit(title_shadow, shadow_rect)

        title_surface = font_large.render("FLAPPY PORK", True, WHITE)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 40))
        screen.blit(title_surface, title_rect)

        box_width, box_height = 260, 45
        box_x = (WIDTH - box_width) // 2
        box_y = (HEIGHT // 2) - 10
        pygame.draw.rect(screen, DARK_GRAY, (box_x, box_y, box_width, box_height), border_radius=5)

        instruct_surface = font_small.render("Press SPACE to Play", True, text_color)
        instruct_rect = instruct_surface.get_rect(center=(WIDTH // 2, box_y + (box_height // 2)))
        screen.blit(instruct_surface, instruct_rect)
        
        hs_surface = font_tiny.render(f"YOUR BEST: {high_score}", True, GOLD)
        hs_rect = hs_surface.get_rect(center=(WIDTH // 2, box_y + box_height + 20))
        pygame.draw.rect(screen, DARK_GRAY, (hs_rect.x - 10, hs_rect.y - 4, hs_rect.width + 20, hs_rect.height + 8), border_radius=4)
        screen.blit(hs_surface, hs_rect)
        
        hover_offset = int(12 * math.sin(animation_timer * 0.07))
        pig.y = (HEIGHT // 2) + 160 + hover_offset
        pig.draw()

    elif current_state == STATE_GAME:
        if not game_over:
            if score < 5:
                current_level = 1
                level_speed = 2      
                level_gap = 160      
            elif score < 15:
                current_level = 2
                level_speed = 3.5    
                level_gap = 135      
            else:
                current_level = 3
                level_speed = 5      
                level_gap = 115      
                
            pig.update(level_speed)
            
            if random.randint(1, 400) == 1 and len(saucepans) == 0:
                saucepans.append(Saucepan(level_speed))
                
            for pan in saucepans:
                pan.update()
                if pan.check_collision(pig):
                    pig.is_bacon = True
                    pig.bacon_timer = 300  
                    score *= 2             
            
            saucepans = [p for p in saucepans if p.x > -40]
            
            for pipe in pipes:
                pipe.speed = level_speed
                pipe.update()
                
                if pipe.hit(pig):
                    if pig.is_bacon:
                        pig.is_bacon = False
                        pig.bacon_timer = 0
                        pig.invincible_frames = 60  
                    else:
                        game_over = True
                        earned_porkoins = 1 + (score // 3)
                        pig.porkoins += earned_porkoins
                        pig.save_universe_data() 
                        
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
                
                if not pipe.passed and pipe.x + pipe.width < 80:
                    pipe.passed = True
                    score += 1
                
            min_pipe_distance = 180 + (level_speed * 25)
            if pipes[-1].x < WIDTH - min_pipe_distance:
                pipes.append(Pipe(level_speed, level_gap))
                
            if pipes[0].x < -60:
                pipes.pop(0)
            
        for pipe in pipes:
            pipe.draw()
        for pan in saucepans:
            pan.draw()
            
        pig.draw_trail()
        pig.draw()

        score_surface = font_large.render(str(score), True, WHITE)
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 50))
        screen.blit(score_surface, score_rect)

        lvl_text = f"LVL {current_level}"
        lvl_color = RED if current_level == 3 else (GOLD if current_level == 2 else WHITE)
        lvl_surface = font_tiny.render(lvl_text, True, lvl_color)
        screen.blit(lvl_surface, (15, 15))

        if game_over:
            over_surface = font_large.render("GAME OVER", True, RED)
            over_rect = over_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(over_surface, over_rect)

            stats_surface = font_tiny.render(f"FINAL SCORE: {score}  |  YOUR BEST: {high_score}", True, WHITE)
            stats_rect = stats_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(stats_surface, stats_rect)

            restart_surface = font_small.render("Press SPACE for Main Menu", True, text_color)
            restart_rect = restart_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            screen.blit(restart_surface, restart_rect)
        
    pygame.display.update()