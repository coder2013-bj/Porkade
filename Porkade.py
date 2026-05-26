import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import json

class PorkadeLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ PORKADE: THE ULTIMATE RETRO CABINET ✨")
        self.root.geometry("700x850")
        self.root.configure(bg="#0f0c1b")

        if getattr(sys, 'frozen', False):
            self.launcher_dir = os.path.dirname(sys.executable)
        else:
            self.launcher_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
        
        self.save_path = os.path.join(self.launcher_dir, "porkade_universe.json")
        
        # Core game data variables
        self.porkoins = 0
        self.unlocked_skins = ["Default"]
        self.equipped_skin = "player_pig.png" # Standardized baseline asset fallback
        self.skin_radio_buttons = {}  # Tracks buttons to update them cleanly
        
        # --- CRITICAL FIX: MAP DISPLAY NAMES TO REAL IMAGES ---
        self.skin_file_mapping = {
            "Default": "player_pig.png",
            "TechnoPig": "TechnoPig.png",
            "Frank the Tank": "FrankTheTank.png",
            "Flappy Salmon": "salmon.png",
            "Lazy Sheep": "sheep_pig.png"
        }
        
        # Create a reverse mapping lookup to handle reading from JSON safely
        self.reverse_skin_mapping = {v: k for k, v in self.skin_file_mapping.items()}
        
        # Shop price configurations
        self.shop_items = {
            "Default": 0,
            "TechnoPig": 100,
            "Frank the Tank": 200,
            "Flappy Salmon": 350,
            "Lazy Sheep": 450
        }

        self.skin_var = tk.StringVar(value="Default")
        
        self.load_universe_data()

        # --- UI Layout: Header ---
        self.header_frame = tk.Frame(root, bg="#1a152e", bd=3, relief="ridge")
        self.header_frame.pack(fill="x", padx=20, pady=15)
        
        self.title_lbl = tk.Label(self.header_frame, text="🕹️ PORKADE CABINET 🕹️", font=("Courier New", 24, "bold"), bg="#1a152e", fg="#ff007f")
        self.title_lbl.pack(pady=5)
        
        self.koin_lbl = tk.Label(self.header_frame, text=f"🪙 PorKoins: {self.porkoins}", font=("Courier New", 14, "bold"), bg="#1a152e", fg="#00f5ff")
        self.koin_lbl.pack(pady=5)

        # --- Game Launcher Frame ---
        self.games_frame = tk.LabelFrame(root, text=" CHOOSE YOUR ARCADE SIMULATION ", font=("Courier New", 12, "bold"), bg="#0f0c1b", fg="#ffffff", bd=2)
        self.games_frame.pack(fill="both", expand=True, padx=20, pady=10)

        button_options = {"font": ("Courier New", 12, "bold"), "fg": "white", "width": 30, "height": 2, "bd": 4, "relief": "raised", "cursor": "hand2"}

        # Store names without extensions here so launch_game can intelligently swap extensions (.exe vs .py)
        games = [
            ("Porky Mart Tycoon", "#2ed573", "porky_mart"),
            ("Angry Pork", "#ff4757", "Angry_pork"),
            ("Crossy Pork", "#1e90ff", "Crossy Pork"),
            ("Flappy Pork", "#ffa502", "Flappy"),
            ("Pork Clicker", "#747d8c", "Pork_clicker")
        ]

        for text, bg_color, base_filename in games:
            btn = tk.Button(self.games_frame, text=text, bg=bg_color, **button_options, command=lambda f=base_filename: self.launch_game(f))
            btn.pack(pady=8)

        # --- Customization/Outfit Shop Frame ---
        self.shop_frame = tk.LabelFrame(root, text=" 🪙 PETER PORK'S OUTFIT CUSTOMIZER ", font=("Courier New", 12, "bold"), bg="#1a152e", fg="#00f5ff", bd=2)
        self.shop_frame.pack(fill="x", padx=20, pady=15)

        # Build the shop interface once cleanly
        self.build_shop_ui()

        # Start background update sync loop
        self.sync_live_wallet_loop()

    def build_shop_ui(self):
        """Clears out and builds the shop layout without recreating the whole cabinet window."""
        for widget in self.shop_frame.winfo_children():
            widget.destroy()
            
        self.skin_radio_buttons.clear()

        for skin_name, price in self.shop_items.items():
            item_frame = tk.Frame(self.shop_frame, bg="#1a152e")
            item_frame.pack(fill="x", padx=15, pady=4)

            if skin_name in self.unlocked_skins:
                rb = tk.Radiobutton(
                    item_frame, text=f"{skin_name} (Unlocked)", variable=self.skin_var, 
                    value=skin_name, bg="#1a152e", fg="#2ed573", font=("Arial", 11),
                    selectcolor="#1a152e", activebackground="#1a152e", activeforeground="#2ed573",
                    command=self.equip_skin
                )
                rb.pack(side="left")
                self.skin_radio_buttons[skin_name] = rb
            else:
                btn_buy = tk.Button(
                    item_frame, text=f"Buy {skin_name} ({price} 🪙)", bg="#ff9f43", fg="black",
                    font=("Arial", 9, "bold"), command=lambda s=skin_name, p=price: self.buy_skin(s, p)
                )
                btn_buy.pack(side="left")

    def launch_game(self, base_name):
        if getattr(sys, 'frozen', False):
            # --- RUNNING AS DISTRIBUTED EXE ---
            game_path = os.path.join(self.launcher_dir, f"{base_name}.exe")
            
            if os.path.exists(game_path):
                try:
                    os.chdir(self.launcher_dir)
                    subprocess.Popen([game_path])
                except Exception as e:
                    messagebox.showerror("Execution Error", f"Failed to start {base_name}.exe:\n{str(e)}")
            else:
                # Local compiled testing fallback: look for script counterparts if binaries aren't baked yet
                py_fallback = os.path.join(self.launcher_dir, f"{base_name}.py")
                if os.path.exists(py_fallback):
                    try:
                        os.chdir(self.launcher_dir)
                        subprocess.Popen(f'cmd.exe /c start "" "{py_fallback}"', shell=True)
                    except Exception as e:
                        messagebox.showerror("Fallback Error", f"Failed to start fallback script:\n{str(e)}")
                else:
                    messagebox.showerror("File Not Found", f"Could not find either:\n- {base_name}.exe\n- {base_name}.py\n\nChecked directory: {self.launcher_dir}")
        else:
            # --- RUNNING IN DEVELOPMENT MODE (THONNY) ---
            game_path = os.path.join(self.launcher_dir, f"{base_name}.py")
            if os.path.exists(game_path):
                try:
                    subprocess.Popen([sys.executable, game_path])
                except Exception as e:
                    messagebox.showerror("Execution Error", f"Failed to launch script inside interpreter:\n{str(e)}")
            else:
                messagebox.showerror("Error", f"Could not locate arcade script:\n{base_name}.py")

    def buy_skin(self, skin_name, price):
        if self.porkoins >= price:
            self.porkoins -= price
            self.unlocked_skins.append(skin_name)
            
            # Use the dictionary mapping to fetch exact image filenames
            self.equipped_skin = self.skin_file_mapping.get(skin_name, "player_pig.png")
            self.skin_var.set(skin_name)
            
            self.save_universe_data()
            self.koin_lbl.config(text=f"🪙 PorKoins: {self.porkoins}")
            self.build_shop_ui() 
        else:
            messagebox.showwarning("Incomplete Funds", "Go earn more PorKoins in Crossy Pork or Pork Clicker!")

    def equip_skin(self):
        # Convert selected shop clean name to true image file path string for sub-games
        selected_display_name = self.skin_var.get()
        self.equipped_skin = self.skin_file_mapping.get(selected_display_name, "player_pig.png")
        self.save_universe_data()

    def load_universe_data(self):
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, "r") as f:
                    data = json.load(f)
                self.porkoins = data.get("porkoins", 0)
                self.unlocked_skins = data.get("unlocked_skins", ["Default"])
                
                raw_skin = data.get("equipped_skin", "player_pig.png")
                # Handle legacy clean name tags versus raw image files
                if raw_skin in self.reverse_skin_mapping:
                    self.equipped_skin = raw_skin
                    self.skin_var.set(self.reverse_skin_mapping[raw_skin])
                elif raw_skin in self.skin_file_mapping:
                    self.equipped_skin = self.skin_file_mapping[raw_skin]
                    self.skin_var.set(raw_skin)
                else:
                    self.equipped_skin = "player_pig.png"
                    self.skin_var.set("Default")
            except Exception: 
                pass

    def save_universe_data(self):
        try:
            with open(self.save_path, "w") as f:
                json.dump({
                    "porkoins": self.porkoins,
                    "unlocked_skins": self.unlocked_skins,
                    "equipped_skin": self.equipped_skin # Writes out exact name like 'techno_pig.png'
                }, f, indent=4)
        except Exception: 
            pass

    def sync_live_wallet_loop(self):
        """Watches for changes made by external sub-games."""
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, "r") as f:
                    data = json.load(f)
                
                new_balance = data.get("porkoins", 0)
                new_unlocked = data.get("unlocked_skins", ["Default"])
                new_equipped_file = data.get("equipped_skin", "player_pig.png")
                
                # Check for wallet balance updates
                if new_balance != self.porkoins:
                    self.porkoins = new_balance
                    self.koin_lbl.config(text=f"🪙 PorKoins: {self.porkoins}")
                
                # If skins were modified elsewhere, safely refresh the shop UI element
                if len(new_unlocked) != len(self.unlocked_skins):
                    self.unlocked_skins = new_unlocked
                    self.build_shop_ui()
                
                # Sync chosen active asset tracker changes made by other scripts
                if new_equipped_file != self.equipped_skin:
                    self.equipped_skin = new_equipped_file
                    mapped_display = self.reverse_skin_mapping.get(new_equipped_file, "Default")
                    self.skin_var.set(mapped_display)
                    
            except Exception: 
                pass
        self.root.after(1000, self.sync_live_wallet_loop)

if __name__ == "__main__":
    window = tk.Tk()
    launcher = PorkadeLauncher(window)
    window.mainloop()