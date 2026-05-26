import tkinter as tk
from tkinter import messagebox
import os
import sys
import json
import random
import math

class MonkeyStylePorkyMart:
    def __init__(self, root):
        self.root = root
        self.root.title("Porky Mart: Mega Tycoon 🛒")
        self.root.geometry("1000x850")  
        self.root.configure(bg="#2f3542")

        # --- Shared Universe Path Logic ---
        if getattr(sys, 'frozen', False):
            self.script_dir = os.path.dirname(sys.executable)
        else:
            self.script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
        
        # Link straight to the global arcade ecosystem save file
        self.universe_save_path = os.path.join(self.script_dir, "porkade_universe.json")

        # --- Core Variables Tied to Universal Wallet ---
        self.porkoins = 150 # Harmonized variable name for ecosystem compatibility
        self.store_level = 1
        self.max_helpers_allowed = 0
        self.equipped_skin = "player_pig.png" # Safe string default fallback
        
        # Expanded 8-Shelf Layout spanning a wider territory
        self.shelves = {
            "shelf_1": {"box": [1100, 150, 1220, 270], "unlocked": True, "stock": 0, "max": 25, "level_req": 1, "y_sort": 250},
            "shelf_2": {"box": [1100, 320, 1220, 440], "unlocked": False, "stock": 0, "max": 25, "level_req": 1, "cost": 80, "y_sort": 420},
            "shelf_3": {"box": [1100, 490, 1220, 610], "unlocked": False, "stock": 0, "max": 25, "level_req": 2, "cost": 200, "y_sort": 590},
            "shelf_4": {"box": [1100, 660, 1220, 780], "unlocked": False, "stock": 0, "max": 30, "level_req": 2, "cost": 400, "y_sort": 760},
            
            "shelf_5": {"box": [1400, 150, 1520, 270], "unlocked": False, "stock": 0, "max": 30, "level_req": 3, "cost": 650, "y_sort": 250},
            "shelf_6": {"box": [1400, 320, 1520, 440], "unlocked": False, "stock": 0, "max": 30, "level_req": 3, "cost": 900, "y_sort": 420},
            "shelf_7": {"box": [1400, 490, 1520, 610], "unlocked": False, "stock": 0, "max": 35, "level_req": 4, "cost": 1400, "y_sort": 590},
            "shelf_8": {"box": [1400, 660, 1520, 780], "unlocked": False, "stock": 0, "max": 40, "level_req": 4, "cost": 2000, "y_sort": 760},
        }

        self.load_universe_data()
        self.player_carrying = 0
        self.max_carry_capacity = 20
        
        self.upgrade_costs = {
            "level_up": [0, 200, 500, 1000, 2500],      
            "hire_helper": [100, 300, 700, 1500, 3000]
        }

        # --- Map & Camera Geometry Settings ---
        self.WORLD_WIDTH = 1600
        self.WORLD_HEIGHT = 1200
        self.camera_x = 0
        self.camera_y = 0
        
        self.player_x = 400
        self.player_y = 500
        self.player_speed = 16

        # --- Complex Grid-World Object Matrix ---
        self.supply_pile = {"box": [100, 100, 260, 240], "stock": 30, "max": 60, "y_sort": 230}
        self.counter = {"box": [700, 500, 840, 620], "cash_pile": 0, "max_cash": 5000, "y_sort": 610}
        
        self.shoppers = []
        self.helpers = []  
        
        # --- CRISP PIXEL ART ASSET LOADER ---
        self.img_player = self.load_and_scale(os.path.join(self.script_dir, self.equipped_skin), zoom_factor=2)
        # If the custom skin failed to load or asset is missing, safely fall back to player_pig.png
        if not self.img_player:
            self.img_player = self.load_and_scale(os.path.join(self.script_dir, "player_pig.png"), zoom_factor=2)

        self.img_shopper = self.load_and_scale(os.path.join(self.script_dir, "customer.png"), zoom_factor=2)
        self.img_box = self.load_and_scale(os.path.join(self.script_dir, "pork_box.png"), shrink_factor=1)
        self.img_shelf = self.load_and_scale(os.path.join(self.script_dir, "shelf.png"), shrink_factor=1)
        self.img_pork = self.load_and_scale(os.path.join(self.script_dir, "pork.png"), shrink_factor=1)   
        self.img_cash = self.load_and_scale(os.path.join(self.script_dir, "cash.png"), shrink_factor=1)   
        self.img_helper = self.load_and_scale(os.path.join(self.script_dir, "helper.png"), shrink_factor=1)
        
        if not self.img_helper and self.img_player:
            self.img_helper = self.load_and_scale(os.path.join(self.script_dir, "player_pig.png"), shrink_factor=1)

        # Re-verify and unpack staff helpers from loaded metadata tracking
        for _ in range(self.max_helpers_allowed):
            self.helpers.append({
                "x": 180, "y": 180, "carrying": 0,  
                "max_capacity": 8, "speed": 8, "target_shelf": "shelf_1"
            })

        # --- UI Interface Assembly ---
        self.top_banner = tk.Frame(root, bg="#1e222b", height=70)
        self.top_banner.pack(fill="x", side="top")
        
        self.title_label = tk.Label(self.top_banner, text="🐷 PORKY MART: MEGA WORLD", font=("Courier New", 20, "bold"), bg="#1e222b", fg="#ffa502")
        self.title_label.pack(side="left", padx=30, pady=15)

        self.money_label = tk.Label(self.top_banner, text=f"💰 Cash: ${self.porkoins}", font=("Courier New", 18, "bold"), bg="#1e222b", fg="#2ed573")
        self.money_label.pack(side="right", padx=30, pady=15)

        self.canvas = tk.Canvas(root, bg="#f6e58d", bd=0, highlightthickness=0) 
        self.canvas.pack(fill="both", expand=True, padx=20, pady=10)

        self.ui_frame = tk.Frame(root, bg="#1e222b", height=100)
        self.ui_frame.pack(fill="x", side="bottom")
        
        self.carry_label = tk.Label(self.ui_frame, text=f"🎒 Carrying: {self.player_carrying}/{self.max_carry_capacity}", font=("Courier New", 14, "bold"), bg="#1e222b", fg="#f1f2f6")
        self.carry_label.pack(side="left", padx=30, pady=30)

        btn_style = {"font": ("Courier New", 12, "bold"), "fg": "white", "bd": 2, "relief": "raised", "padx": 15, "pady": 8, "cursor": "hand2", "activebackground": "#2f3542"}
        
        self.btn_hire = tk.Button(self.ui_frame, text="Hire Helper", bg="#ff9f43", **btn_style, command=self.hire_helper)
        self.btn_hire.pack(side="right", padx=20, pady=25)
        
        self.btn_expand = tk.Button(self.ui_frame, text="Expand Store", bg="#0984e3", **btn_style, command=self.expand_store)
        self.btn_expand.pack(side="right", padx=10, pady=25)

        self.update_ui_buttons()

        # Keyboard Control Bindings
        self.root.bind("<KeyPress>", self.handle_movement)
        
        # Spawners & Loops
        self.spawn_shopper_loop()
        self.passive_supply_generation() 
        self.update_game_frame()

    def load_and_scale(self, path, zoom_factor=1, shrink_factor=1):
        if os.path.exists(path):
            try:
                img = tk.PhotoImage(file=path)
                if zoom_factor > 1: img = img.zoom(zoom_factor, zoom_factor)
                if shrink_factor > 1: img = img.subsample(shrink_factor, shrink_factor)
                return img
            except Exception:
                return None
        return None

    def load_universe_data(self):
        if os.path.exists(self.universe_save_path):
            try:
                with open(self.universe_save_path, "r") as f:
                    data = json.load(f)
                    self.porkoins = data.get("porkoins", 150)
                    self.store_level = data.get("mart_store_level", 1)
                    self.max_helpers_allowed = data.get("mart_max_helpers", 0)
                    
                    # FIXED: Now querying using a correct literal string key 
                    self.equipped_skin = data.get("equipped_skin", "player_pig.png")
                    
                    saved_shelves = data.get("mart_shelves", {})
                    for k, unlocked in saved_shelves.items():
                        if k in self.shelves:
                            self.shelves[k]["unlocked"] = unlocked
                    return
            except Exception: 
                pass

    def save_universe_data(self):
        data = {}
        if os.path.exists(self.universe_save_path):
            try:
                with open(self.universe_save_path, "r") as f: data = json.load(f)
            except Exception: pass
            
        data["porkoins"] = self.porkoins
        data["mart_store_level"] = self.store_level
        data["mart_max_helpers"] = self.max_helpers_allowed
        data["equipped_skin"] = self.equipped_skin  # Preserve skin choices on save
        data["mart_shelves"] = {k: v["unlocked"] for k, v in self.shelves.items()}
        
        try:
            with open(self.universe_save_path, "w") as f: json.dump(data, f, indent=4)
        except Exception: pass

    def update_ui_buttons(self):
        if self.max_helpers_allowed < len(self.upgrade_costs["hire_helper"]):
            cost = self.upgrade_costs["hire_helper"][self.max_helpers_allowed]
            self.btn_hire.config(text=f"👨‍🏭 Hire Staff (${cost})", state="normal", bg="#ff9f43")
        else:
            self.btn_hire.config(text="Staff Maxed!", state="disabled", bg="#747d8c")

        if self.store_level < 5:
            cost = self.upgrade_costs["level_up"][self.store_level]
            self.btn_expand.config(text=f"🚀 Expand (Lvl {self.store_level+1}) (${cost})", state="normal", bg="#0984e3")
        else:
            self.btn_expand.config(text="Max Tier Reached!", state="disabled", bg="#747d8c")

    def handle_movement(self, event):
        key = event.keysym.lower()
        new_x, new_y = self.player_x, self.player_y
        
        if key in ["w", "up"]: new_y -= self.player_speed
        elif key in ["s", "down"]: new_y += self.player_speed
        elif key in ["a", "left"]: new_x -= self.player_speed
        elif key in ["d", "right"]: new_x += self.player_speed
            
        if 40 <= new_x <= self.WORLD_WIDTH - 40 and 40 <= new_y <= self.WORLD_HEIGHT - 40:
            self.player_x, self.player_y = new_x, new_y
            
        self.check_collision_zones(is_player=True, entity=self)

    def check_collision_zones(self, is_player, entity):
        ex, ey = (entity.player_x, entity.player_y) if is_player else (entity["x"], entity["y"])
        
        bx1, by1, bx2, by2 = self.supply_pile["box"]
        if bx1 <= ex <= bx2 and by1 <= ey <= by2:
            if is_player:
                if self.player_carrying < self.max_carry_capacity and self.supply_pile["stock"] > 0:
                    self.player_carrying += 1
                    self.supply_pile["stock"] -= 1
            else:
                if entity["carrying"] < entity["max_capacity"] and self.supply_pile["stock"] > 0:
                    entity["carrying"] += 1
                    self.supply_pile["stock"] -= 1
                    return

        for s_id, shelf in self.shelves.items():
            sx1, sy1, sx2, sy2 = shelf["box"]
            if not shelf["unlocked"]:
                if is_player and self.store_level >= shelf["level_req"]:
                    if sx1 <= ex <= sx2 and sy1 <= ey <= sy2 and self.porkoins >= shelf["cost"]:
                        self.porkoins -= shelf["cost"]
                        shelf["unlocked"] = True
                        self.save_universe_data()
                continue
                
            if sx1 <= ex <= sx2 and sy1 <= ey <= sy2:
                if is_player:
                    if self.player_carrying > 0 and shelf["stock"] < shelf["max"]:
                        self.player_carrying -= 1
                        shelf["stock"] += 1
                else:
                    if entity["carrying"] > 0 and shelf["stock"] < shelf["max"]:
                        entity["carrying"] -= 1
                        shelf["stock"] += 1
                        return

        cx1, cy1, cx2, cy2 = self.counter["box"]
        if cx1 <= ex <= cx2 and cy1 <= ey <= cy2 and is_player:
            if self.counter["cash_pile"] > 0:
                self.porkoins += self.counter["cash_pile"]
                self.counter["cash_pile"] = 0
                self.save_universe_data()

    def hire_helper(self):
        if self.max_helpers_allowed < len(self.upgrade_costs["hire_helper"]):
            cost = self.upgrade_costs["hire_helper"][self.max_helpers_allowed]
            if self.porkoins >= cost:
                self.porkoins -= cost
                self.max_helpers_allowed += 1
                self.helpers.append({
                    "x": 180, "y": 180, 
                    "carrying": 0, "max_capacity": 8, 
                    "speed": 8, "target_shelf": "shelf_1"
                })
                self.update_ui_buttons()
                self.save_universe_data()

    def expand_store(self):
        if self.store_level < 5:
            cost = self.upgrade_costs["level_up"][self.store_level]
            if self.porkoins >= cost:
                self.porkoins -= cost
                self.store_level += 1
                self.update_ui_buttons()
                self.save_universe_data()

    def passive_supply_generation(self):
        if self.supply_pile["stock"] < self.supply_pile["max"]:
            self.supply_pile["stock"] += (2 + (self.store_level // 2))
        self.root.after(1500, self.passive_supply_generation)

    def draw_pixel_shadow(self, rx, ry, width):
        height = width / 2.5
        self.canvas.create_oval(rx - width, ry - height, rx + width, ry + height, fill="#eccc68", outline="")

    def update_game_frame(self):
        self.canvas.delete("all")
        
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w < 10: canvas_w, canvas_h = 960, 680 
        
        self.camera_x = self.player_x - (canvas_w // 2)
        self.camera_y = self.player_y - (canvas_h // 2)
        
        self.camera_x = max(0, min(self.camera_x, self.WORLD_WIDTH - canvas_w))
        self.camera_y = max(0, min(self.camera_y, self.WORLD_HEIGHT - canvas_h))

        # Ground Borders
        g_x1, g_y1 = 15 - self.camera_x, 15 - self.camera_y
        g_x2, g_y2 = (self.WORLD_WIDTH - 15) - self.camera_x, (self.WORLD_HEIGHT - 15) - self.camera_y
        self.canvas.create_rectangle(g_x1, g_y1, g_x2, g_y2, fill="#ffffff", outline="#f1f2f6", width=8)

        # LAYER 1: Shadow Buffers
        sb = self.supply_pile["box"]
        self.draw_pixel_shadow(((sb[0]+sb[2])//2) - self.camera_x, ((sb[1]+sb[3])//2 + 25) - self.camera_y, 45)
        
        cb = self.counter["box"]
        self.draw_pixel_shadow(((cb[0]+cb[2])//2) - self.camera_x, ((cb[1]+cb[3])//2 + 30) - self.camera_y, 60)
        
        for s_id, shelf in self.shelves.items():
            if shelf["unlocked"]:
                box = shelf["box"]
                self.draw_pixel_shadow(((box[0]+box[2])//2) - self.camera_x, ((box[1]+box[3])//2 + 25) - self.camera_y, 50)

        for w in self.helpers:
            self.draw_pixel_shadow(w["x"] - self.camera_x, (w["y"] + 20) - self.camera_y, 22)
        for s in self.shoppers:
            self.draw_pixel_shadow(s["x"] - self.camera_x, (s["y"] + 24) - self.camera_y, 25)
        self.draw_pixel_shadow(self.player_x - self.camera_x, (self.player_y + 26) - self.camera_y, 28)

        # LAYER 2: Y-Sorting Layout Compilation
        render_queue = []
        render_queue.append({"y": self.supply_pile["y_sort"], "type": "supply", "data": self.supply_pile})
        render_queue.append({"y": self.counter["y_sort"], "type": "counter", "data": self.counter})
        
        for s_id, shelf in self.shelves.items():
            render_queue.append({"y": shelf["y_sort"], "type": "shelf", "data": shelf, "id": s_id})

        for worker in self.helpers:
            self.run_helper_ai(worker)
            render_queue.append({"y": worker["y"], "type": "helper", "data": worker})
            
        for shopper in self.shoppers:
            self.animate_shopper_ai(shopper)
            render_queue.append({"y": shopper["y"], "type": "shopper", "data": shopper})
            
        render_queue.append({"y": self.player_y, "type": "player", "data": None})

        # Depth sorting alignment
        render_queue.sort(key=lambda obj: obj["y"])

        # LAYER 3: Render Pipe Execution Loop
        for item in render_queue:
            t = item["type"]
            
            if t == "supply":
                s = item["data"]
                b = s["box"]
                rx1, ry1, rx2, ry2 = b[0]-self.camera_x, b[1]-self.camera_y, b[2]-self.camera_x, b[3]-self.camera_y
                self.canvas.create_rectangle(rx1, ry1, rx2, ry2, fill="#a55eee", outline="#8854d0", width=4)
                if self.img_box:
                    self.canvas.create_image((rx1+rx2)//2, (ry1+ry2)//2, image=self.img_box)
                prog = s["stock"] / s["max"]
                self.canvas.create_rectangle(rx1, ry2+10, rx2, ry2+16, fill="#dcdde1", outline="")
                self.canvas.create_rectangle(rx1, ry2+10, rx1 + (prog * (rx2-rx1)), ry2+16, fill="#a55eee", outline="")

            elif t == "counter":
                c = item["data"]
                b = c["box"]
                rx1, ry1, rx2, ry2 = b[0]-self.camera_x, b[1]-self.camera_y, b[2]-self.camera_x, b[3]-self.camera_y
                self.canvas.create_rectangle(rx1, ry1, rx2, ry2, fill="#ff4757", outline="#ff6b81", width=4)
                
                mx, my = (rx1+rx2)//2, (ry1+ry2)//2
                if c["cash_pile"] > 0:
                    stacks = min(8, max(1, c["cash_pile"] // 50))
                    for idx in range(stacks):
                        if self.img_cash:
                            self.canvas.create_image(mx, my - (idx * 6), image=self.img_cash)
                else:
                    self.canvas.create_text(mx, my, text="CASHIER", font=("Courier New", 11, "bold"), fill="white")
                self.canvas.create_text(mx, ry2+20, text=f"${c['cash_pile']}", font=("Courier New", 12, "bold"), fill="#2f3542")

            elif t == "shelf":
                shelf = item["data"]
                b = shelf["box"]
                rx1, ry1, rx2, ry2 = b[0]-self.camera_x, b[1]-self.camera_y, b[2]-self.camera_x, b[3]-self.camera_y
                mx, my = (rx1+rx2)//2, (ry1+ry2)//2
                
                if shelf["unlocked"]:
                    if self.img_shelf:
                        self.canvas.create_image(mx, my, image=self.img_shelf)
                    else:
                        self.canvas.create_rectangle(rx1, ry1, rx2, ry2, fill="#f0932b", outline="#e056fd", width=3)
                    
                    if shelf["stock"] > 0 and self.img_pork:
                        meat_cnt = min(8, shelf["stock"])
                        for idx in range(meat_cnt):
                            col = idx % 4
                            row = idx // 4
                            self.canvas.create_image(rx1 + 16 + (col * 23), ry1 + 24 + (row * 18), image=self.img_pork)
                    
                    prog = shelf["stock"] / shelf["max"]
                    self.canvas.create_rectangle(rx1, ry2+10, rx2, ry2+15, fill="#dcdde1", outline="")
                    self.canvas.create_rectangle(rx1, ry2+10, rx1 + (prog * (rx2-rx1)), ry2+15, fill="#2ed573", outline="")
                else:
                    if self.store_level >= shelf["level_req"]:
                        self.canvas.create_rectangle(rx1, ry1, rx2, ry2, fill="#f1f2f6", outline="#ffa502", width=3, dash=(6, 3))
                        self.canvas.create_text(mx, my, text=f"UNLOCK\n${shelf['cost']}", font=("Courier New", 10, "bold"), fill="#ff7f50")
                    else:
                        self.canvas.create_rectangle(rx1, ry1, rx2, ry2, fill="#747d8c", outline="#2f3542")
                        self.canvas.create_text(mx, my, text=f"🔒 Lvl {shelf['level_req']}", font=("Courier New", 10, "bold"), fill="white")

            elif t == "helper":
                w = item["data"]
                rx, ry = w["x"] - self.camera_x, w["y"] - self.camera_y
                if self.img_helper:
                    self.canvas.create_image(rx, ry, image=self.img_helper)
                if w["carrying"] > 0:
                    self.canvas.create_rectangle(rx-8, ry-26, rx+8, ry-21, fill="#78e08f", outline="white")

            elif t == "shopper":
                s = item["data"]
                rx, ry = s["x"] - self.camera_x, s["y"] - self.camera_y
                if self.img_shopper:
                    self.canvas.create_image(rx, ry, image=self.img_shopper)
                
                if s["demand_remaining"] > 0 and not s["has_bought_all"]:
                    self.canvas.create_rectangle(rx-14, ry-34, rx+14, ry-22, fill="#2ed573", outline="white")
                    self.canvas.create_text(rx, ry-28, text=f"x{s['demand_remaining']}", font=("Arial", 9, "bold"), fill="white")

            elif t == "player":
                rx, ry = self.player_x - self.camera_x, self.player_y - self.camera_y
                if self.img_player:
                    self.canvas.create_image(rx, ry, image=self.img_player)
                if self.player_carrying > 0:
                    for idx in range(min(8, self.player_carrying)):
                        self.canvas.create_rectangle(rx-18, ry-36-(idx*6), rx+18, ry-30-(idx*6), fill="#78e08f", outline="#38ea60", width=1)

        # Sync Interface Panel Strings
        self.money_label.config(text=f"💰 Cash: ${self.porkoins}")
        self.carry_label.config(text=f"🎒 Inventory: {self.player_carrying}/{self.max_carry_capacity}")
        self.root.after(30, self.update_game_frame)

    def run_helper_ai(self, helper):
        unlocked_shelves = [k for k, v in self.shelves.items() if v["unlocked"]]
        if not unlocked_shelves: return

        if helper["carrying"] < helper["max_capacity"]:
            tx, ty = 180, 180
            if self.supply_pile["stock"] == 0 and helper["carrying"] > 0:
                helper["target_shelf"] = random.choice(unlocked_shelves)
        else:
            target = helper["target_shelf"]
            if target not in unlocked_shelves or self.shelves[target]["stock"] >= self.shelves[target]["max"]:
                helper["target_shelf"] = random.choice(unlocked_shelves)
                target = helper["target_shelf"]
            sb = self.shelves[target]["box"]
            tx, ty = (sb[0]+sb[2])//2, (sb[1]+sb[3])//2

        dx, dy = tx - helper["x"], ty - helper["y"]
        dist = math.hypot(dx, dy)
        if dist > helper["speed"]:
            helper["x"] += (dx / dist) * helper["speed"]
            helper["y"] += (dy / dist) * helper["speed"]
        else:
            helper["x"], helper["y"] = tx, ty
            self.check_collision_zones(is_player=False, entity=helper)

    def spawn_shopper_loop(self):
        max_shoppers_allowed = 6 + (self.store_level * 3) 
        unlocked_shelves = [k for k, v in self.shelves.items() if v["unlocked"]]
        
        if len(self.shoppers) < max_shoppers_allowed and unlocked_shelves:
            items_wanted = random.randint(1, 4)
            self.shoppers.append({
                "x": 750, "y": 1100, 
                "target": random.choice(unlocked_shelves), 
                "demand_remaining": items_wanted,
                "has_bought_all": False,
                "items_in_hand": 0
            })
        self.root.after(2000, self.spawn_shopper_loop)

    def animate_shopper_ai(self, shopper):
        unlocked_shelves = [k for k, v in self.shelves.items() if v["unlocked"]]
        
        if not shopper["has_bought_all"]:
            target_id = shopper["target"]
            if target_id not in unlocked_shelves:
                shopper["target"] = random.choice(unlocked_shelves) if unlocked_shelves else "exit"
                return
                
            sb = self.shelves[target_id]["box"]
            tx, ty = sb[0] - 45, (sb[1]+sb[3])//2
            
            self.move_towards(shopper, tx, ty, speed=6)
            if abs(shopper["x"] - tx) <= 8 and abs(shopper["y"] - ty) <= 8:
                if self.shelves[target_id]["stock"] > 0:
                    self.shelves[target_id]["stock"] -= 1
                    shopper["demand_remaining"] -= 1
                    shopper["items_in_hand"] += 1
                    
                    if shopper["demand_remaining"] <= 0:
                        shopper["has_bought_all"] = True
                        shopper["target"] = "register"
                    else:
                        shopper["target"] = random.choice(unlocked_shelves)
                else:
                    shopper["target"] = random.choice(unlocked_shelves)
                    
        elif shopper["target"] == "register":
            tx, ty = 660, 560
            self.move_towards(shopper, tx, ty, speed=6)
            if abs(shopper["x"] - tx) <= 8 and abs(shopper["y"] - ty) <= 8:
                self.counter["cash_pile"] += (shopper["items_in_hand"] * 35)
                shopper["target"] = "exit"
                
        elif shopper["target"] == "exit":
            self.move_towards(shopper, 750, 1150, speed=7)
            if shopper["y"] >= 1100:
                self.shoppers.remove(shopper)

    def move_towards(self, entity, tx, ty, speed):
        if entity["x"] > tx: entity["x"] -= speed
        if entity["x"] < tx: entity["x"] += speed
        if entity["y"] > ty: entity["y"] -= speed
        if entity["y"] < ty: entity["y"] += speed

if __name__ == "__main__":
    window = tk.Tk()
    game = MonkeyStylePorkyMart(window)
    window.mainloop()