import pygame
import random
import sys
import os
import json

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
FPS = 60
ROW_HEIGHT = 50  # Strict Grid-Based Geometry
LANE_COUNT = (SCREEN_HEIGHT // ROW_HEIGHT) + 2

# Colors
GREEN = (142, 204, 114)
DARK_GREEN = (119, 181, 91)
GREY = (110, 116, 125)
BLUE = (105, 196, 219)
WHITE = (255, 255, 255)
RED = (235, 77, 75)
YELLOW = (241, 196, 15)
BLACK = (0, 0, 0)

# Setup Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Crossy Pork: Infinite Scrolling Edition")
clock = pygame.time.Clock()

def load_and_scale(filename, size):
    """Safely loads custom assets or handles an identical flat-art fallback."""
    if os.path.exists(filename):
        try:
            img = pygame.image.load(filename).convert_alpha()
            return pygame.transform.scale(img, size)
        except Exception:
            pass
    surf = pygame.Surface(size, pygame.SRCALPHA)
    if filename == "pig.png":
        surf.fill((255, 182, 193))
        pygame.draw.rect(surf, (255, 105, 180), [size[0]-15, size[1]//3, 15, 15])
    elif filename == "car.png":
        surf.fill(random.choice([RED, YELLOW, (52, 152, 219)]))
        pygame.draw.rect(surf, (44, 62, 80), [5, 5, size[0]-10, 10])
    elif filename == "log.png":
        surf.fill((139, 69, 19))
        pygame.draw.rect(surf, (101, 50, 14), [0, 0, size[0], 5])
    return surf

PIG_IMG = load_and_scale("pig.png", (36, 36))
CAR_IMG_BASE = load_and_scale("car.png", (80, 36))
LOG_IMG = load_and_scale("log.png", (140, 36))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if getattr(sys, 'frozen', False):
            self.script_dir = os.path.dirname(sys.executable)
        else:
            self.script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
        
        self.universe_save_path = os.path.join(self.script_dir, "porkade_universe.json")
        self.porkoins = 0
        self.equipped_skin = "Default" 
        self.load_universe_data()
        
        self.image = PIG_IMG
        if self.equipped_skin not in ["Default", "player_pig.png"]:
            player_image_path = os.path.join(self.script_dir, self.equipped_skin)
            if os.path.exists(player_image_path):
                try:
                    raw_img = pygame.image.load(player_image_path).convert_alpha()
                    self.image = pygame.transform.scale(raw_img, (36, 36))
                except Exception:
                    pass
        
        self.rect = self.image.get_rect()
        self.reset()
        
    def load_universe_data(self):
        if os.path.exists(self.universe_save_path):
            try:
                with open(self.universe_save_path, "r") as f:
                    data = json.load(f)
                    self.porkoins = data.get("porkoins", 0)
                    self.equipped_skin = data.get("equipped_skin", "Default")
            except Exception:
                pass

    def reset(self):
        self.grid_x = SCREEN_WIDTH // 2
        self.grid_y = SCREEN_HEIGHT - 100
        self.rect.x = self.grid_x - self.rect.width // 2
        self.rect.y = self.grid_y + (ROW_HEIGHT - self.rect.height) // 2

    def move(self, dx, dy):
        next_x = self.grid_x + dx
        next_y = self.grid_y + dy
        if 0 < next_x < SCREEN_WIDTH and next_y < SCREEN_HEIGHT:
            self.grid_x = next_x
            self.grid_y = next_y
            self.rect.x = self.grid_x - self.rect.width // 2
            self.rect.y = self.grid_y + (ROW_HEIGHT - self.rect.height) // 2

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, lane_id, lane_type, direction, speed):
        super().__init__()
        self.lane_id = lane_id  
        self.lane_type = lane_type  
        self.direction = direction  
        self.speed = speed
        
        if self.lane_type == "road":
            # Correct asset rotation matching their driving direction vectors
            if self.direction == 1:
                self.image = pygame.transform.flip(CAR_IMG_BASE, True, False)
            else:
                self.image = CAR_IMG_BASE
        else:
            self.image = LOG_IMG
            
        self.rect = self.image.get_rect()
        if self.direction == 1:
            self.rect.x = -self.rect.width - random.randint(10, 300)
        else:
            self.rect.x = SCREEN_WIDTH + random.randint(10, 300)

    def update_position(self, camera_y, lanes_dict):
        # Update scrolling position based on its structural lane index identity
        y_pos = lanes_dict[self.lane_id]["y"] - camera_y
        self.rect.y = y_pos + (ROW_HEIGHT - self.rect.height) // 2
        
        # Linear tracking movement
        self.rect.x += self.speed * self.direction
        if self.direction == 1 and self.rect.left > SCREEN_WIDTH:
            self.rect.x = -self.rect.width - random.randint(50, 150)
        elif self.direction == -1 and self.rect.right < 0:
            self.rect.x = SCREEN_WIDTH + random.randint(50, 150)

class Eagle(pygame.sprite.Sprite):
    def __init__(self, target_y):
        super().__init__()
        self.image = pygame.Surface((90, 55), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (47, 53, 66), [(0, 27), (55, 0), (90, 27), (55, 55)])
        pygame.draw.polygon(self.image, (241, 196, 15), [(0, 27), (20, 20), (20, 34)])
        self.rect = self.image.get_rect()
        self.rect.x = -200
        self.rect.y = target_y - 10
        self.speed = 24

    def update(self):
        self.rect.x += self.speed

def show_game_over_screen(final_score):
    font_large = pygame.font.SysFont("Impact", 60)
    font_small = pygame.font.SysFont("Arial", 30)
    
    go_text = font_large.render("GAME OVER", True, RED)
    score_text = font_small.render(f"Final Score: {final_score}", True, WHITE)
    retry_text = font_small.render("Press SPACE to Restart or ESC to Quit", True, YELLOW)
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        screen.fill(BLACK)
        screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
        pygame.display.flip()
        clock.tick(15)

def main():
    while True:
        player = Player()
        obstacles = pygame.sprite.Group()
        
        # --- INFINITE PROCEDURAL GENERATION ENGINE ---
        lanes_dict = {}
        next_lane_id = 0
        lowest_lane_y = SCREEN_HEIGHT - ROW_HEIGHT
        
        # Generate initial base grid layout
        for i in range(LANE_COUNT):
            y_coord = lowest_lane_y - (i * ROW_HEIGHT)
            l_type = "grass" if i < 3 else random.choice(["grass", "road", "road", "river"])
            lanes_dict[next_lane_id] = {"y": y_coord, "type": l_type}
            
            if l_type in ["road", "river"]:
                direction = random.choice([-1, 1])
                speed = random.uniform(2.0, 4.0)
                obstacles.add(Obstacle(next_lane_id, l_type, direction, speed))
                obstacles.add(Obstacle(next_lane_id, l_type, direction, speed + random.uniform(0.5, 1.2)))
            next_lane_id += 1

        score = 0
        highest_score_row = 0
        camera_y = 0
        target_camera_y = 0
        highest_y = player.grid_y
        
        eagle_triggered = False
        eagle = None
        game_lost = False
        running = True
        time_since_move = 0

        while running:
            time_since_move += 1
            
            # Anti-idle tracking limit check
            if time_since_move > 250 and not eagle_triggered:
                eagle_triggered = True
                eagle = Eagle(player.rect.y)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN and not eagle_triggered:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        player.move(0, -ROW_HEIGHT)
                        time_since_move = 0
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        player.move(0, ROW_HEIGHT)
                        time_since_move = 0
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        player.move(-ROW_HEIGHT, 0)
                        time_since_move = 0
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        player.move(ROW_HEIGHT, 0)
                        time_since_move = 0

            # Calculate Row Score based on distance from baseline
            current_row_score = (SCREEN_HEIGHT - 100 - player.grid_y) // ROW_HEIGHT
            if current_row_score > highest_score_row:
                score += (current_row_score - highest_score_row)
                highest_score_row = current_row_score

            # --- DYNAMIC FIXED CAMERA SYSTEM ---
            if player.grid_y < highest_y:
                highest_y = player.grid_y
            
            target_camera_y = highest_y - (SCREEN_HEIGHT // 2)
            camera_y += (target_camera_y - camera_y) * 0.1

            # --- FIXED INFINITE ROW RECYCLING SYSTEM ---
            for l_id in list(lanes_dict.keys()):
                if lanes_dict[l_id]["y"] - camera_y > SCREEN_HEIGHT + ROW_HEIGHT:
                    
                    topmost_y = min(lane["y"] for lane in lanes_dict.values())
                    new_y = topmost_y - ROW_HEIGHT
                        
                    new_type = random.choice(["grass", "road", "road", "river", "river"])
                    lanes_dict[l_id] = {"y": new_y, "type": new_type}
                    
                    # Clean obsolete entities
                    for obs in list(obstacles):
                        if obs.lane_id == l_id:
                            obstacles.remove(obs)
                            
                    # Inject fresh obstacles into reconstituted map lanes
                    if new_type in ["road", "river"]:
                        direction = random.choice([-1, 1])
                        speed = random.uniform(2.0, 4.5) + (score * 0.02)  # Difficulty multiplier
                        obstacles.add(Obstacle(l_id, new_type, direction, speed))
                        obstacles.add(Obstacle(l_id, new_type, direction, speed + random.uniform(0.6, 1.4)))

            for obs in obstacles:
                obs.update_position(camera_y, lanes_dict)

            # Draw Map Layout Structure
            screen.fill(DARK_GREEN)
            for l_id, lane in lanes_dict.items():
                y_pixel = lane["y"] - camera_y
                if -ROW_HEIGHT <= y_pixel <= SCREEN_HEIGHT:
                    render_rect = [0, y_pixel, SCREEN_WIDTH, ROW_HEIGHT]
                    if lane["type"] == "grass":
                        pygame.draw.rect(screen, GREEN, render_rect)
                    elif lane["type"] == "road":
                        pygame.draw.rect(screen, GREY, render_rect)
                        pygame.draw.rect(screen, WHITE, [0, y_pixel + ROW_HEIGHT - 2, SCREEN_WIDTH, 2])
                    elif lane["type"] == "river":
                        pygame.draw.rect(screen, BLUE, render_rect)

            obstacles.draw(screen)
            
            player.rect.y = player.grid_y - camera_y + (ROW_HEIGHT - player.rect.height) // 2

            # Identify structural cell environmental boundaries
            current_lane_type = "grass"
            for l_id, lane in lanes_dict.items():
                if lane["y"] <= player.grid_y < lane["y"] + ROW_HEIGHT:
                    current_lane_type = lane["type"]

            # Log Drift Mechanics
            on_log = False
            if current_lane_type == "river" and not eagle_triggered:
                for obs in obstacles:
                    if obs.lane_type == "river" and obs.rect.colliderect(player.rect):
                        player.grid_x += obs.speed * obs.direction
                        player.rect.x = player.grid_x - player.rect.width // 2
                        on_log = True
                        break
                if not on_log or player.rect.right < 0 or player.rect.left > SCREEN_WIDTH:
                    game_lost = True
                    running = False

            # Road Hazard Collision Check
            if current_lane_type == "road" and not eagle_triggered:
                for obs in obstacles:
                    if obs.lane_type == "road" and obs.rect.colliderect(player.rect):
                        game_lost = True
                        running = False

            # Dropoff boundary limits check
            if player.rect.top > SCREEN_HEIGHT:
                game_lost = True
                running = False

            # Render Screen / Process Active Eagle Mechanics
            if not eagle_triggered:
                screen.blit(player.image, player.rect)
            else:
                eagle.update()
                screen.blit(eagle.image, eagle.rect)
                
                if eagle.rect.colliderect(player.rect) or eagle.rect.x > player.rect.x:
                    player.rect.x = eagle.rect.x + 10
                    player.rect.y = eagle.rect.y + 10
                    screen.blit(player.image, player.rect)
                    
                if eagle.rect.x > SCREEN_WIDTH + 150:
                    game_lost = True
                    running = False

            # Draw HUD
            font = pygame.font.SysFont("Impact", 36)
            score_surface = font.render(str(score), True, WHITE)
            screen.blit(score_surface, (25, 20))

            pygame.display.flip()
            clock.tick(FPS)

        if game_lost:
            show_game_over_screen(score)

if __name__ == "__main__":
    main()