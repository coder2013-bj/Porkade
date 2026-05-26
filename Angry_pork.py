import pygame
import pymunk
import math
import sys
import json
import os
import random

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Angry Pork: The Butcher Rebellion ⚔️")
clock = pygame.time.Clock()

# Game States
STATE_MENU = 0
STATE_GAME = 1
STATE_VICTORY = 2
STATE_GAMEOVER = 3
current_state = STATE_MENU

# Colors
BG_COLOR = (220, 240, 255)
SLING_COLOR = (100, 50, 20)
WOOD_COLOR = (190, 130, 70)
WOOD_BORDER = (130, 80, 30)
GROUND_Y = HEIGHT - 50 
TEXT_COLOR = (40, 40, 80)
ARC_COLOR = (120, 140, 160)

# Fonts
font_title = pygame.font.SysFont("Arial", 54, bold=True)
font_ui = pygame.font.SysFont("Arial", 24, bold=True)

# Prevents butchers from taking physics damage until a pig is fired
level_started = False

# Determine Directory Paths for Assets & Unified Universe Save Data
if getattr(sys, 'frozen', False):
    launcher_dir = os.path.dirname(sys.executable)
else:
    launcher_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
universe_save_path = os.path.join(launcher_dir, "porkade_universe.json")

# --- Persistent Shared Universe Profile Data System ---
def load_universe_data():
    default_data = {
        "porkoins": 0, 
        "unlocked_skins": ["Default"], 
        "equipped_skin": "Default",
        "angry_pork_level": 1
    }
    if os.path.exists(universe_save_path):
        try:
            with open(universe_save_path, "r") as f:
                data = json.load(f)
                if "angry_pork_level" not in data:
                    data["angry_pork_level"] = 1
                if "porkoins" not in data:
                    data["porkoins"] = 0
                return data
        except Exception:
            pass
    return default_data

def save_universe_data(data):
    try:
        with open(universe_save_path, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

def award_porkoins(amount):
    global match_porkoins_earned
    data = load_universe_data()
    data["porkoins"] = data.get("porkoins", 0) + amount
    match_porkoins_earned += amount  
    save_universe_data(data)

def save_level_progress(lvl):
    data = load_universe_data()
    data["angry_pork_level"] = lvl
    save_universe_data(data)

# Read initialization files immediately upon boot
universe_profile = load_universe_data()
current_level = universe_profile["angry_pork_level"]
match_porkoins_earned = 0  

# Helper asset function
def load_sprite_safely(filename, size_radius, fallback_color):
    full_path = os.path.join(launcher_dir, filename)
    if os.path.exists(full_path):
        try:
            img = pygame.image.load(full_path).convert_alpha()
            return pygame.transform.scale(img, (size_radius * 2, size_radius * 2))
        except Exception: pass
    return None

# Physics Space Setup
space = pymunk.Space()
space.gravity = (0, 900)

# Solid Floor Plane
ground = pymunk.Body(body_type=pymunk.Body.STATIC)
ground_shape = pymunk.Segment(ground, (0, GROUND_Y), (WIDTH, GROUND_Y), 10)
ground_shape.friction = 1.0
ground_shape.elasticity = 0.0  
space.add(ground, ground_shape)

# Game Entities
blocks = []
tnt_barrels = []
enemies = []
ammo_porks = []
explosions = []

current_pork_idx = 0
tracked_pig = None  # TRACKING FIX: Keeps eyes on the flying pig exclusively
sling_pos = (200, GROUND_Y - 150)
is_dragging = False


class ButcherTarget:
    def __init__(self, x, y, is_king=False):
        self.is_king = is_king
        self.radius = 45 if is_king else 22
        self.hp = 5.0 if is_king else 1.0
        self.max_hp = self.hp
        
        mass = 80 if is_king else 10
        self.body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, self.radius))
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.friction = 0.6
        self.shape.elasticity = 0.2
        space.add(self.body, self.shape)
        
        default_file = "king_butcher.png" if self.is_king else "butcher.png"
        fallback_color = (150, 0, 0) if self.is_king else (230, 70, 70)
        self.sprite = load_sprite_safely(default_file, self.radius, fallback_color)

    def draw(self, surface):
        pos = int(self.body.position.x), int(self.body.position.y)
        if self.sprite:
            surface.blit(self.sprite, (pos[0] - self.radius, pos[1] - self.radius))
        else:
            base_color = (180, 40, 40) if self.is_king else (220, 100, 100)
            pygame.draw.circle(surface, base_color, pos, self.radius)
            pygame.draw.circle(surface, (0, 0, 0), pos, self.radius, 2)
            
        if self.is_king:
            bar_w = 90
            bar_x = pos[0] - (bar_w // 2)
            bar_y = pos[1] - self.radius - 15
            pygame.draw.rect(surface, (100, 20, 20), (bar_x, bar_y, bar_w, 8))
            health_pct = max(0.0, self.hp / self.max_hp)
            pygame.draw.rect(surface, (50, 210, 100), (bar_x, bar_y, int(bar_w * health_pct), 8))


class TNTBarrel:
    def __init__(self, x, y):
        self.radius = 24
        self.body = pymunk.Body(15, float('inf'))
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.friction = 0.8
        space.add(self.body, self.shape)
        self.triggered = False

    def draw(self, surface):
        pos = int(self.body.position.x), int(self.body.position.y)
        pygame.draw.circle(surface, (230, 70, 50), pos, self.radius)
        pygame.draw.circle(surface, (60, 20, 20), pos, self.radius, 2)
        txt = font_ui.render("TNT", True, (255, 255, 255))
        surface.blit(txt, (pos[0] - txt.get_width() // 2, pos[1] - txt.get_height() // 2))


class ProjectilePork:
    def __init__(self, x, y, p_type="Standard"):
        self.p_type = p_type
        self.launched = False 
        
        if p_type == "Cyber Fast":
            self.mass, self.radius, self.color = 8, 16, (240, 200, 30)
        elif p_type == "Heavy Boulder":
            self.mass, self.radius, self.color = 45, 30, (130, 140, 150)
        else:
            self.mass, self.radius, self.color = 15, 20, (255, 160, 190)

        self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass, 0, self.radius), body_type=pymunk.Body.STATIC)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.friction = 0.65
        space.add(self.body, self.shape)
        
        # --- SKIN REGISTRY LOADER ---
        profile = load_universe_data()
        equipped_skin = profile.get("equipped_skin", "Default")
        
        asset_filename = "angrypig.png" if equipped_skin == "Default" else equipped_skin
        skin_path = os.path.join(launcher_dir, asset_filename)
        
        self.sprite = None
        if os.path.exists(skin_path):
            try:
                raw_img = pygame.image.load(skin_path).convert_alpha()
                image_rect = raw_img.get_bounding_rect()
                cropped_subsurface = raw_img.subsurface(image_rect)
                scaled_img = pygame.transform.scale(cropped_subsurface, (self.radius * 2, self.radius * 2))
                self.sprite = pygame.transform.flip(scaled_img, True, False)
            except Exception as e:
                print(f"Failed to process custom skin for projectile: {e}")
                
        if not self.sprite:
            self.sprite = load_sprite_safely("angrypig.png", self.radius, self.color)

    def draw(self, surface):
        bx, by = self.body.position.x, self.body.position.y
        if math.isnan(bx) or math.isnan(by):
            return
        pos = int(bx), int(by)
        if self.sprite:
            surface.blit(self.sprite, (pos[0] - self.radius, pos[1] - self.radius))
        else:
            pygame.draw.circle(surface, self.color, pos, self.radius)
            pygame.draw.circle(surface, (0, 0, 0), pos, self.radius, 2)


def draw_trajectory_arc(surface, start_pos, mouse_pos):
    dx = sling_pos[0] - mouse_pos[0]
    dy = sling_pos[1] - mouse_pos[1]
    vx = dx * 7.5
    vy = dy * 7.5
    gravity = 900
    
    points = []
    for i in range(30):
        t = i * 0.03  
        x = mouse_pos[0] + vx * t
        y = mouse_pos[1] + vy * t + 0.5 * gravity * (t ** 2)
        if y >= GROUND_Y:
            break
        points.append((int(x), int(y)))
        
    for pt in points:
        pygame.draw.circle(surface, ARC_COLOR, pt, 3)

def create_wood_block(x, y, w, h, angle=0):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = x, y
    body.angle = math.radians(angle)
    shape = pymunk.Poly.create_box(body, (w, h))
    shape.friction = 0.8  
    shape.elasticity = 0.05  
    space.add(body, shape)
    
    blocks.append({
        "body": body, 
        "shape": shape, 
        "w": w, 
        "h": h, 
        "hp": 1.2, 
        "is_active_dynamic": False,
        "mass": 15,
        "moment": pymunk.moment_for_box(15, (w, h))
    })

def activate_block_physics(b):
    if b["is_active_dynamic"]:
        return
    b["is_active_dynamic"] = True
    
    old_pos = b["body"].position
    old_angle = b["body"].angle
    
    space.remove(b["body"], b["shape"])
    
    b["body"] = pymunk.Body(b["mass"], b["moment"], body_type=pymunk.Body.DYNAMIC)
    b["body"].position = old_pos
    b["body"].angle = old_angle
    
    b["shape"] = pymunk.Poly.create_box(b["body"], (b["w"], b["h"]))
    b["shape"].friction = 0.8
    b["shape"].elasticity = 0.05
    
    space.add(b["body"], b["shape"])

def init_procedural_level(lvl):
    global blocks, tnt_barrels, enemies, ammo_porks, current_pork_idx, tracked_pig, match_porkoins_earned, level_started
    
    for b in blocks: space.remove(b["body"], b["shape"])
    for t in tnt_barrels: space.remove(t.body, t.shape)
    for e in enemies: space.remove(e.body, e.shape)
    for p in ammo_porks: space.remove(p.body, p.shape)
    
    blocks.clear()
    tnt_barrels.clear()
    enemies.clear()
    ammo_porks.clear()
    current_pork_idx = 0
    tracked_pig = None
    match_porkoins_earned = 0 
    level_started = False  

    is_boss_stage = (lvl % 50 == 0)

    if is_boss_stage:
        enemies.append(ButcherTarget(950, GROUND_Y - 60, is_king=True))
        for col in [820, 880, 1060]:
            for row in range(8):
                create_wood_block(col, GROUND_Y - 35 - (row * 65), 35, 55)
        create_wood_block(940, GROUND_Y - 560, 310, 25)
        tnt_barrels.append(TNTBarrel(940, GROUND_Y - 590))
    else:
        layout_style = random.choice(["towers", "pyramid", "shelf"])

        if layout_style == "towers":
            tower_height = min(4 + (lvl // 5), 7)
            base_x1, base_x2 = 850, 1050
            
            stilt_w, stilt_h = 30, 70
            slab_w, slab_h = 260, 25

            for row in range(tower_height):
                y_stilt = GROUND_Y - (stilt_h // 2) - (row * (stilt_h + slab_h + 4))
                
                create_wood_block(base_x1, y_stilt, stilt_w, stilt_h)
                create_wood_block(base_x2, y_stilt, stilt_w, stilt_h)
                
                y_slab = y_stilt - (stilt_h // 2) - (slab_h // 2) - 2
                create_wood_block((base_x1 + base_x2) // 2, y_slab, slab_w, slab_h)
                
                enemies.append(ButcherTarget((base_x1 + base_x2) // 2, y_slab - (slab_h // 2) - 24, is_king=False))
                
            tnt_barrels.append(TNTBarrel((base_x1 + base_x2) // 2, GROUND_Y - 30))

        elif layout_style == "pyramid":
            center_x = 950
            levels = min(3 + (lvl // 8), 5)
            
            block_w = 80
            block_h = 25
            x_spacing = block_w + 8  
            y_spacing = block_h + 6  

            for r in range(levels):
                blocks_in_row = levels - r
                y_pos = GROUND_Y - (block_h // 2) - 4 - (r * y_spacing)
                row_width = (blocks_in_row - 1) * x_spacing
                start_x = center_x - (row_width // 2)
                
                for c in range(blocks_in_row):
                    bx = start_x + (c * x_spacing)
                    create_wood_block(bx, y_pos, block_w, block_h, angle=0)
                    
                    if r < levels - 1 and c % 2 == 0:
                        enemies.append(ButcherTarget(bx, y_pos - 35, is_king=False))
            tnt_barrels.append(TNTBarrel(center_x, GROUND_Y - 40))

        elif layout_style == "shelf":
            center_x = 920
            create_wood_block(800, GROUND_Y - 80, 50, 150, angle=0)
            create_wood_block(1040, GROUND_Y - 80, 50, 150, angle=0)
            create_wood_block(920, GROUND_Y - 175, 340, 30, angle=0)
            
            enemies.append(ButcherTarget(850, GROUND_Y - 215, is_king=False))
            enemies.append(ButcherTarget(990, GROUND_Y - 215, is_king=False))
            tnt_barrels.append(TNTBarrel(920, GROUND_Y - 215))

    ammo_count = 5 if is_boss_stage else 3
    for i in range(ammo_count):
        p_type = "Standard"
        if i == 1: p_type = "Cyber Fast"
        elif i >= 2 and i % 2 == 0: p_type = "Heavy Boulder"
        
        start_pos = sling_pos if i == 0 else (sling_pos[0] - (i * 45), GROUND_Y - 20)
        ammo_porks.append(ProjectilePork(start_pos[0], start_pos[1], p_type))

init_procedural_level(current_level)

# --- MAIN LOOP ---
while True:
    screen.fill(BG_COLOR)
    mx, my = pygame.mouse.get_pos()

    pygame.draw.rect(screen, (70, 140, 70), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.line(screen, SLING_COLOR, sling_pos, (sling_pos[0], GROUND_Y), 8)

    if current_state == STATE_MENU:
        profile = load_universe_data()
        total_porkoins = profile.get("porkoins", 0)

        t_lbl = font_title.render("ANGRY PORK: REBELLION CAMPAIGN", True, TEXT_COLOR)
        s_lbl = font_ui.render(f"Press SPACE to launch Level {current_level}", True, TEXT_COLOR)
        p_lbl = font_ui.render(f"Total Shared Wallet: {total_porkoins} Porkoins 🐷", True, (230, 130, 30))
        
        screen.blit(t_lbl, (WIDTH // 2 - t_lbl.get_width() // 2, HEIGHT // 3 - 30))
        screen.blit(s_lbl, (WIDTH // 2 - s_lbl.get_width() // 2, HEIGHT // 2))
        screen.blit(p_lbl, (WIDTH // 2 - p_lbl.get_width() // 2, HEIGHT // 2 + 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                current_state = STATE_GAME

    elif current_state == STATE_GAME:
        active_pork = ammo_porks[current_pork_idx] if current_pork_idx < len(ammo_porks) else None

        if is_dragging and active_pork:
            pygame.draw.line(screen, (255, 80, 80), sling_pos, (int(active_pork.body.position.x), int(active_pork.body.position.y)), 4)
            draw_trajectory_arc(screen, sling_pos, active_pork.body.position)

        # FIXED COLLISION RADAR: Evaluates the actual flying pig target, not the bench queue
        if tracked_pig and tracked_pig.launched:
            px, py = tracked_pig.body.position.x, tracked_pig.body.position.y
            pig_velocity = tracked_pig.body.velocity
            
            for b in blocks:
                if not b["is_active_dynamic"]:
                    dist = math.hypot(b["body"].position.x - px, b["body"].position.y - py)
                    # Use a slightly wider buffer to catch the dynamic crossover perfectly
                    if dist < (max(b["w"], b["h"]) // 2 + tracked_pig.radius + 12):
                        activate_block_physics(b)
                        # Deliver structural impulse directly from impact velocity vectors
                        b["body"].apply_impulse_at_local_point(pig_velocity * b["mass"] * 1.2)

        # TNT Explosions
        for tnt in list(tnt_barrels):
            if level_started and not tnt.triggered and (abs(tnt.body.velocity.x) > 15 or abs(tnt.body.velocity.y) > 15):
                tnt.triggered = True
                explosions.append({"x": tnt.body.position.x, "y": tnt.body.position.y, "radius": 10, "max_radius": 220})
                award_porkoins(20)

                for b in blocks:
                    dist = math.hypot(b["body"].position.x - tnt.body.position.x, b["body"].position.y - tnt.body.position.y)
                    if dist < 220:
                        activate_block_physics(b)
                        b["hp"] -= 2.0
                        b["body"].apply_impulse_at_local_point((b["body"].position - tnt.body.position).normalized() * 65000)

                for e in enemies:
                    dist = math.hypot(e.body.position.x - tnt.body.position.x, e.body.position.y - tnt.body.position.y)
                    if dist < 220:
                        e.hp -= 5.0

                space.remove(tnt.body, tnt.shape)
                tnt_barrels.remove(tnt)

        # Wood Blocks Update
        for b in list(blocks):
            pos = b["body"].position
            
            if b["is_active_dynamic"]:
                v_speed = math.hypot(b["body"].velocity.x, b["body"].velocity.y)
                if v_speed > 25:
                    for other_b in blocks:
                        if not other_b["is_active_dynamic"]:
                            d = math.hypot(other_b["body"].position.x - pos.x, other_b["body"].position.y - pos.y)
                            if d < max(b["w"], b["h"]) + 20:
                                activate_block_physics(other_b)

                if v_speed > 30:
                    b["hp"] -= 0.15  
                    if b["hp"] <= 0:
                        space.remove(b["body"], b["shape"])
                        blocks.remove(b)
                        award_porkoins(1)
                        continue
            
            rect_surface = pygame.Surface((b["w"], b["h"]), pygame.SRCALPHA)
            rect_surface.fill(WOOD_COLOR)
            pygame.draw.rect(rect_surface, WOOD_BORDER, (0, 0, b["w"], b["h"]), 2)
            
            rot_surface = pygame.transform.rotate(rect_surface, math.degrees(-b["body"].angle))
            new_rect = rot_surface.get_rect(center=(int(pos.x), int(pos.y)))
            screen.blit(rot_surface, new_rect.topleft)

        # Enemies Update & Projectile Hit Checks
        for e in list(enemies):
            v_impact = math.hypot(e.body.velocity.x, e.body.velocity.y)
            
            if level_started and v_impact > 20:
                e.hp -= (v_impact * 0.08)
                
            if tracked_pig and tracked_pig.launched:
                dist_to_pig = math.hypot(e.body.position.x - tracked_pig.body.position.x, e.body.position.y - tracked_pig.body.position.y)
                if dist_to_pig < (e.radius + tracked_pig.radius + 10):
                    pig_speed = math.hypot(tracked_pig.body.velocity.x, tracked_pig.body.velocity.y)
                    if pig_speed > 30:
                        e.hp -= (pig_speed * 0.1)

            if level_started and e.hp <= 0:
                explosions.append({"x": e.body.position.x, "y": e.body.position.y, "radius": 5, "max_radius": 50})
                award_porkoins(100 if e.is_king else 25)
                space.remove(e.body, e.shape)
                enemies.remove(e)
            else:
                e.draw(screen)

        for tnt in tnt_barrels: tnt.draw(screen)
        for pork in ammo_porks: pork.draw(screen)

        # Explosions Update
        for exp in list(explosions):
            pygame.draw.circle(screen, (255, 150, 50), (int(exp["x"]), int(exp["y"])), int(exp["radius"]), 3)
            exp["radius"] += 8
            if exp["radius"] >= exp["max_radius"]: explosions.remove(exp)

        # HUD Details
        stage_title = f"LEVEL {current_level} - KING BUTCHER BOSS BATTLE ⚔️" if (current_level % 50 == 0) else f"LEVEL {current_level} - REBELS VS BUTCHERS"
        screen.blit(font_ui.render(stage_title, True, TEXT_COLOR), (20, 20))
        screen.blit(font_ui.render(f"Earned This Run: +{match_porkoins_earned} Porkoins 🐷", True, (210, 100, 30)), (20, 50))

        if level_started and len(enemies) == 0:
            current_state = STATE_VICTORY
            save_level_progress(current_level + 1)
        elif current_pork_idx >= len(ammo_porks) and tracked_pig and abs(tracked_pig.body.velocity.x) < 1.5 and not is_dragging:
            current_state = STATE_GAMEOVER

        # Mechanics Listeners
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and active_pork and not is_dragging:
                p_pos = active_pork.body.position
                if math.hypot(mx - p_pos.x, my - p_pos.y) < active_pork.radius + 30:
                    is_dragging = True
                    
            if event.type == pygame.MOUSEBUTTONUP and is_dragging and active_pork:
                is_dragging = False
                launch_x, launch_y = active_pork.body.position.x, active_pork.body.position.y
                
                space.remove(active_pork.body, active_pork.shape)
                active_pork.body = pymunk.Body(active_pork.mass, pymunk.moment_for_circle(active_pork.mass, 0, active_pork.radius), body_type=pymunk.Body.DYNAMIC)
                active_pork.body.position = launch_x, launch_y
                active_pork.shape = pymunk.Circle(active_pork.body, active_pork.radius)
                active_pork.shape.friction = 0.65
                space.add(active_pork.body, active_pork.shape)
                
                dx, dy = sling_pos[0] - launch_x, sling_pos[1] - launch_y
                active_pork.body.velocity = (dx * 7.5, dy * 7.5)
                active_pork.launched = True 
                
                # Assign to tracker immediately before advancing indices
                tracked_pig = active_pork
                level_started = True 
                
                current_pork_idx += 1
                if current_pork_idx < len(ammo_porks):
                    ammo_porks[current_pork_idx].body.position = sling_pos

        if is_dragging and active_pork:
            dist = math.hypot(mx - sling_pos[0], my - sling_pos[1])
            if dist > 150:
                angle = math.atan2(my - sling_pos[1], mx - sling_pos[0])
                active_pork.body.position = sling_pos[0] + 150 * math.cos(angle), sling_pos[1] + 150 * math.sin(angle)
            else:
                active_pork.body.position = mx, my

        space.step(1 / 60.0)

    elif current_state == STATE_VICTORY:
        win_txt = font_title.render("STAGE COMPLETED!", True, (40, 160, 40))
        sub_txt = font_ui.render("Press SPACE to advance floors", True, TEXT_COLOR)
        reward_txt = font_ui.render(f"Level Total Collected: +{match_porkoins_earned} Porkoins!", True, (220, 110, 20))
        
        screen.blit(win_txt, (WIDTH // 2 - win_txt.get_width() // 2, HEIGHT // 3 - 20))
        screen.blit(reward_txt, (WIDTH // 2 - reward_txt.get_width() // 2, HEIGHT // 2 - 20))
        screen.blit(sub_txt, (WIDTH // 2 - sub_txt.get_width() // 2, HEIGHT // 2 + 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                current_level += 1
                init_procedural_level(current_level)
                current_state = STATE_GAME

    elif current_state == STATE_GAMEOVER:
        lose_txt = font_title.render("MISSION FAILED!", True, (200, 40, 40))
        sub_txt = font_ui.render("Press 'R' to rebuild map components and retry", True, TEXT_COLOR)
        keep_txt = font_ui.render(f"Secured from rubble: {match_porkoins_earned} Porkoins", True, (130, 80, 40))
        
        screen.blit(lose_txt, (WIDTH // 2 - lose_txt.get_width() // 2, HEIGHT // 3 - 20))
        screen.blit(keep_txt, (WIDTH // 2 - keep_txt.get_width() // 2, HEIGHT // 2 - 20))
        screen.blit(sub_txt, (WIDTH // 2 - sub_txt.get_width() // 2, HEIGHT // 2 + 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                init_procedural_level(current_level)
                current_state = STATE_GAME

    pygame.display.flip()
    clock.tick(60)