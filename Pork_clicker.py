import tkinter as tk
from tkinter import messagebox
import os
import sys
import json
import random

class PorkClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Pork Clicker 🐷")
        self.root.geometry("450x780")
        self.root.configure(bg="#2c3e50")
        
        # --- UNIVERSAL TRACKING AND PATH RESOLUTION ---
        if getattr(sys, 'frozen', False):
            self.script_dir = os.path.dirname(sys.executable)
        else:
            self.script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
        
        self.universe_save_path = os.path.join(self.script_dir, "porkade_universe.json")
        
        # --- CORE LOCAL & GLOBAL SAVING VARIABLE INFRASTRUCTURE ---
        self.porkoins = 0
        self.pork_count = 0        # CRITICAL FIX: Restored core tracking variable to stop crash loop
        self.pork_per_click = 1
        self.pork_per_second = 0
        self.equipped_skin = "player_pig.png" 

        # Upgrade parameters matching your operational milestones
        self.mud_cost = 10
        self.mud_count = 0

        self.feeder_cost = 15
        self.feeder_count = 0
        self.feeder_pps = 1

        self.farm_cost = 100
        self.farm_count = 0
        self.farm_pps = 8

        self.factory_cost = 1100
        self.factory_count = 0
        self.factory_pps = 12

        self.more_food_cost = 1000
        self.more_food_count = 0

        # Sync master universe state metadata values prior to layout assembly
        self.load_universe_data()
        
        # --- DYNAMIC IMAGE LOADER ---
        # Interlocks layout structures with your Peter Pork Outfits Customizer shop selection
        player_image_path = os.path.join(self.script_dir, self.equipped_skin)
        
        if os.path.exists(player_image_path):
            self.pig_image = tk.PhotoImage(file=player_image_path)
            # Create particle-sized variations dynamically from chosen cosmetic file string
            try:
                self.mini_pig_image = self.pig_image.subsample(4, 4)
            except Exception:
                self.mini_pig_image = None
        else:
            print(f"Warning: Asset {self.equipped_skin} missing. Falling back to default.")
            # Hardcoded fallbacks if file systems fail to align properly
            fallback_path = os.path.join(self.script_dir, "player_pig.png")
            if os.path.exists(fallback_path):
                self.pig_image = tk.PhotoImage(file=fallback_path)
                self.mini_pig_image = self.pig_image.subsample(4, 4)
            else:
                self.pig_image = None
                self.mini_pig_image = None

        # --- High-Performance Particle Engine Array ---
        self.falling_porks = []

        # --- UI Assembly Elements ---
        self.score_label = tk.Label(root, text=f"{self.pork_count} Pork", font=("Arial", 28, "bold"), bg="#2c3e50", fg="#f1c40f")
        self.score_label.pack(pady=10)

        self.pps_label = tk.Label(root, text=f"per second: {self.pork_per_second}", font=("Arial", 14), bg="#2c3e50", fg="#ecf0f1")
        self.pps_label.pack(pady=5)

        # Main interactive visual arena canvas panel
        self.canvas = tk.Canvas(root, width=400, height=280, bg="#2c3e50", highlightthickness=0)
        self.canvas.pack(pady=15)
        
        # Render Central Action Character Target
        if self.pig_image:
            self.center_pig = self.canvas.create_image(200, 140, image=self.pig_image)
        else:
            self.center_pig = self.canvas.create_oval(110, 50, 290, 230, fill="#e84393", outline="#fd79a8", width=4)
            self.canvas.create_text(200, 140, text="TAP!", font=("Arial", 24, "bold"), fill="white")

        # Map mouse interface click coordinates
        self.canvas.bind("<Button-1>", lambda event: self.click_pig())

        # --- Control Upgrade Buttons Panel Layout ---
        self.btn_mud = tk.Button(root, text="", font=("Arial", 10, "bold"), bg="#34495e", fg="white", command=self.buy_mud)
        self.btn_mud.pack(fill="x", padx=30, pady=5)

        self.btn_feeder = tk.Button(root, text="", font=("Arial", 10, "bold"), bg="#34495e", fg="white", command=self.buy_feeder)
        self.btn_feeder.pack(fill="x", padx=30, pady=5)

        self.btn_farm = tk.Button(root, text="", font=("Arial", 10, "bold"), bg="#34495e", fg="white", command=self.buy_farm)
        self.btn_farm.pack(fill="x", padx=30, pady=5)

        self.btn_factory = tk.Button(root, text="", font=("Arial", 10, "bold"), bg="#34495e", fg="white", command=self.buy_factory)
        self.btn_factory.pack(fill="x", padx=30, pady=5)

        self.btn_food = tk.Button(root, text="", font=("Arial", 10, "bold"), bg="#34495e", fg="white", command=self.buy_more_food)
        self.btn_food.pack(fill="x", padx=30, pady=5)

        # Pull system visual refreshes straight to buttons
        self.update_displays()
        
        # Launch isolated animation frame processing updates
        self.auto_pork_loop()
        self.particle_physics_loop()

    def spawn_pork_particle(self, count=1):
        """Injects running particle mini assets into the canvas frame system."""
        for _ in range(count):
            start_x = random.randint(10, 390)
            start_y = random.randint(-40, -5)
            fall_speed = random.uniform(3.0, 7.5)
            
            if self.mini_pig_image:
                p_id = self.canvas.create_image(start_x, start_y, image=self.mini_pig_image)
            else:
                p_id = self.canvas.create_oval(start_x, start_y, start_x+10, start_y+10, fill="#fd79a8", outline="")
                
            # Keep drops rendering stacked smoothly behind the primary button asset
            self.canvas.tag_lower(p_id, self.center_pig)
            
            self.falling_porks.append({
                "id": p_id,
                "x": start_x,
                "y": start_y,
                "speed": fall_speed
            })

    def click_pig(self):
        self.pork_count += self.pork_per_click
        
        # Give currency rewards directly to the wallet for actively clicking
        if self.pork_count % 10 == 0:
            self.porkoins += 1
            
        self.spawn_pork_particle(count=max(1, min(self.pork_per_click, 5)))
        self.update_displays()
        self.save_universe_data()

    def buy_mud(self):
        if self.pork_count >= self.mud_cost:
            self.pork_count -= self.mud_cost
            self.mud_count += 1
            self.pork_per_click += 1
            self.mud_cost = int(self.mud_cost * 1.3)
            self.update_displays()
            self.save_universe_data()
        else:
            messagebox.showwarning("Not Enough Pork", f"Requires {self.mud_cost} Pork! Click your pig to build assets.")

    def buy_feeder(self):
        if self.pork_count >= self.feeder_cost:
            self.pork_count -= self.feeder_cost
            self.feeder_count += 1
            self.pork_per_second += self.feeder_pps
            self.feeder_cost = int(self.feeder_cost * 1.3)
            self.update_displays()
            self.save_universe_data()
        else:
            messagebox.showwarning("Not Enough Pork", "Earn more pork production clicks to unlock this feeding system!")

    def buy_farm(self):
        if self.pork_count >= self.farm_cost:
            self.pork_count -= self.farm_cost
            self.farm_count += 1
            self.pork_per_second += self.farm_pps
            self.farm_cost = int(self.farm_cost * 1.25)
            self.update_displays()
            self.save_universe_data()
        else:
            messagebox.showwarning("Not Enough Pork", "Operational infrastructure demands higher click values!")

    def buy_factory(self):
        if self.pork_count >= self.factory_cost:
            self.pork_count -= self.factory_cost
            self.factory_count += 1
            self.pork_per_second += self.factory_pps
            self.factory_cost = int(self.factory_cost * 1.35)
            self.update_displays()
            self.save_universe_data()
        else:
            messagebox.showwarning("Not Enough Pork", "Industrial automated structures require more capital investment!")

    def buy_more_food(self):
        if self.pork_count >= self.more_food_cost:
            self.pork_count -= self.more_food_cost
            self.more_food_count += 1
            self.pork_per_click += 4
            self.more_food_cost = int(self.more_food_cost * 1.4)
            self.update_displays()
            self.save_universe_data()
        else:
            messagebox.showwarning("Not Enough Pork", "Premium nutrition reserves are currently unaffordable!")

    def update_displays(self):
        self.score_label.config(text=f"{self.pork_count} Pork")
        self.pps_label.config(text=f"per second: {self.pork_per_second} | Wallet: {self.porkoins} 🪙")
        self.btn_mud.config(text=f"Buy Golden Mud ({self.mud_cost} Pork) [+1/Click] Owned: {self.mud_count}")
        self.btn_feeder.config(text=f"Buy Auto-Feeder ({self.feeder_cost} Pork) [+1/sec] Owned: {self.feeder_count}")
        self.btn_farm.config(text=f"Buy Pig Farm ({self.farm_cost} Pork) [+8/sec] Owned: {self.farm_count}")
        self.btn_factory.config(text=f"Buy Factory Farm ({self.factory_cost} Pork) [+12/sec] Owned: {self.factory_count}")
        self.btn_food.config(text=f"Buy More Food ({self.more_food_cost} Pork) [+4/Click] Owned: {self.more_food_count}")

    def auto_pork_loop(self):
        """Processes continuous background engine yields safely across timeline tracks."""
        if self.pork_per_second > 0:
            self.pork_count += self.pork_per_second
            
            # Automated yields passive generation kickback to the centralized profile wallet
            if self.pork_count % 25 < self.pork_per_second:
                self.porkoins += 1
                
            self.update_displays()
            self.save_universe_data()
            
            # Animate falling object drops based directly on production strength metrics
            spawn_amt = min(20, max(1, self.pork_per_second // 3))
            self.spawn_pork_particle(count=spawn_amt)
            
        self.root.after(1000, self.auto_pork_loop)

    def particle_physics_loop(self):
        """Processes high frequency vector shifts for tumbling drop rendering components."""
        active_porks = []
        
        for p in self.falling_porks:
            p["y"] += p["speed"]
            try:
                self.canvas.coords(p["id"], p["x"], p["y"])
                if p["y"] < 300:
                    active_porks.append(p)
                else:
                    self.canvas.delete(p["id"])
            except Exception:
                pass
                
        self.falling_porks = active_porks
        
        if self.pork_per_second > 0 and len(self.falling_porks) < (self.pork_per_second * 2):
            if random.random() < 0.35:
                self.spawn_pork_particle(count=1)
                
        self.root.after(30, self.particle_physics_loop)

    def load_universe_data(self):
        if os.path.exists(self.universe_save_path):
            try:
                with open(self.universe_save_path, "r") as f:
                    data = json.load(f)
                
                self.porkoins = data.get("porkoins", 0)
                self.equipped_skin = data.get("equipped_skin", "player_pig.png")
                
                # Fetch persistent interior progression states cleanly
                self.pork_count = data.get("clicker_pork_count", 0)
                self.pork_per_click = data.get("clicker_per_click", 1)
                self.pork_per_second = data.get("clicker_pps", 0)
                self.mud_cost = data.get("clicker_mud_cost", 10)
                self.mud_count = data.get("clicker_mud_count", 0)
                self.feeder_cost = data.get("clicker_feeder_cost", 15)
                self.feeder_count = data.get("clicker_feeder_count", 0)
                self.farm_cost = data.get("clicker_farm_cost", 100)
                self.farm_count = data.get("clicker_farm_count", 0)
                self.factory_cost = data.get("clicker_factory_cost", 1100)
                self.factory_count = data.get("clicker_factory_count", 0)
                self.more_food_cost = data.get("clicker_food_cost", 1000)
                self.more_food_count = data.get("clicker_food_count", 0)
                
            except Exception as e:
                print(f"Error reading master registry file: {e}")

    def save_universe_data(self):
        try:
            data = {}
            if os.path.exists(self.universe_save_path):
                with open(self.universe_save_path, "r") as f:
                    try:
                        data = json.load(f)
                    except Exception:
                        pass

            data["porkoins"] = self.porkoins
            data["equipped_skin"] = self.equipped_skin

            # Inject localized game module progress values safely
            data["clicker_pork_count"] = self.pork_count
            data["clicker_per_click"] = self.pork_per_click
            data["clicker_pps"] = self.pork_per_second
            data["clicker_mud_cost"] = self.mud_cost
            data["clicker_mud_count"] = self.mud_count
            data["clicker_feeder_cost"] = self.feeder_cost
            data["clicker_feeder_count"] = self.feeder_count
            data["clicker_farm_cost"] = self.farm_cost
            data["clicker_farm_count"] = self.farm_count
            data["clicker_factory_cost"] = self.factory_cost
            data["clicker_factory_count"] = self.factory_count
            data["clicker_food_cost"] = self.more_food_cost
            data["clicker_food_count"] = self.more_food_count

            with open(self.universe_save_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to compile save state data packet: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PorkClicker(root)
    root.mainloop()