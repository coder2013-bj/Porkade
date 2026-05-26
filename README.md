# 🎮 THE PORKADE ECOSYSTEM

Welcome to **The Porkade**, an interconnected, porcine-centric suite of arcade, clicker, and management simulator applications.

This ecosystem is currently in active development by **Barney Jack**. Feel free to dive into the arcade, explore the source architecture, and run the programs locally.

---

## 🛑 IMPORTANT DEPLOYMENT & USAGE NOTICE

* **Code Preservation:** You are highly encouraged to explore, review, and read through the source code directories to see how the system operates. However, **please do not edit, modify, or rewrite the codebase** without explicit coordination.
* **Device Restrictions:** These applications are tightly integrated. **Please do not copy, distribute, or port them to other devices** without the author's express prior consent.
* **Licensing:** This entire ecosystem is protected under the **Creative Commons Attribution-NoDerivatives 4.0 International (CC-BY-ND)** license. You may share and run the material in its current form, but if you remix, transform, or build upon the material, you may not distribute the modified material.

---

## 🗺️ Ecosystem & Architecture Overview

The Porkade does not operate as a single monolithic application. Instead, it utilizes a decoupled, parent-child process architecture to isolate game logic, performance loops, and asset paths.

```
                   ┌───────────────────────────────┐
                   │   Porkade Master Control Deck │
                   │         (Porkade.py)          │
                   └───────────────┬───────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │ (subprocess.Popen)      │ (subprocess.Popen)      │ (subprocess.Popen)
         ▼                         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   Flappy Pork    │      │    Angry Pork    │      │    Crossy Pork   │
│ (In Development) │      │ (Deep Dev/⚠️Lock) │      │  (Child Module)  │
└──────────────────┘      └──────────────────┘      └──────────────────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   ▼
                   ┌───────────────────────────────┐
                   │     Shared Asset Registry     │
                   │   (.ico, .png, .json saves)   │
                   └───────────────────────────────┘

```

### 1. The Master Control Deck (`Porkade.py`)

The primary launchpad interface. It serves exclusively as an administrative hub and master orchestration dashboard. It manages the global UI loop but delegates game calculations (item production, asset inflation, queuing loops) to independent, localized runtime modules.

### 2. Path Inversion & Absolute Directory Containment

To prevent relative pathing bugs across fluctuating environments, the suite tracks its environment contexts dynamically:

* **Frozen Executable State:** Uses `sys.executable` discovery hooks to locate physical assets relative to the compiled `.exe`.
* **Scripted Dev State:** Tracks positions via system arguments (`sys.argv[0]`) or absolute global paths (`__file__`) to isolate assets directly inside the folder where execution originated, avoiding system-default user profile directories.

### 3. Subprocess Isolation & Working Directory (`cwd`) Compliance

When launching secondary modules—such as *Flappy Pork*, *Angry Pork*, *Crossy Pork*, *Pork Clicker*, or *Porky Mart*—the master launcher explicitly instantiates separate process threads. All calls initiated via Python’s `subprocess.Popen` explicitly declare a Current Working Directory (`cwd`) parameter pointing exactly to that specific child module’s workspace folder. This guarantees that files like `pig_sprite.png` or `Bird.ico` resolve flawlessly within their own sandboxes.

---

## 💾 Save State Architecture & Local Data Validation

Progress data across the ecosystem is maintained completely locally through structured JavaScript Object Notation (`.json`) files (e.g., `save_data.json` for clicker components and `mart_save.json` for commercial tycoons).

### Save File Schema Structure

```json
{
  "pork_count": 1450,
  "pork_per_second": 8,
  "pork_per_click": 5,
  "feeder_cost": 25,
  "farm_cost": 140,
  "mud_cost": 112,
  "factory_cost": 210,
  "shed_cost": 105,
  "feeder_count": 2,
  "farm_count": 1,
  "mud_count": 3,
  "factory_count": 0,
  "shed_count": 1
}

```

### ⚠️ Troubleshooting Directory Displacement & Hard Resets

If deleting your `save_data.json` fails to wipe your in-game scores, the host machine has likely cached or generated the file within an alternative development tree path (such as your IDE's root installation folder).

To bypass this and execute a **Force-Overwrite**, apply the following development interception workflow:

1. Locate the core instance initialization method (`__init__`) of the target game.
2. Prepend a comment block indicator (`#`) to the active save retrieval routine: `# self.load_game()`.
3. Directly underneath it, inject a temporary serialization command: `self.save_game()`.
4. Run the code exactly once to generate a clean, uninflated save file over the true active path.
5. Revert the code back to its original production structure.

---

## 📈 In-Game Fiscal Policies & Inflation Coefficients

All economic modules use exponential inflation coefficients to simulate late-stage resource scaling. Every time an asset tier is procured, its base cost updates dynamically:

$$New\ Cost = \lfloor Current\ Cost \times Inflation\ Factor \rfloor$$

The system uses absolute truncation logic (`int()`) to drop remaining floating-point decimals from the newly generated cost integer, preventing fractional token corruption.

| Asset ID | Base Unit Cost | Production Value | Compounding Inflation Factor |
| --- | --- | --- | --- |
| **Auto-Feeder** | 15 Pork | +1 Pork / Second | 1.3x Compound Rate |
| **Golden Mud** | 50 Pork | +1 Pork / Click | 1.5x Compound Rate |
| **Shed Structure** | 75 Pork | +4 Pork / Click | 1.4x Compound Rate |
| **Pig Farm** | 100 Pork | +8 Pork / Second | 1.4x Compound Rate |
| **Factory Farm** | 150 Pork | +12 Pork / Second | 1.4x Compound Rate |

> 📌 **Fiscal Disclaimer:** All currencies, assets, and points generated across this software suite are strictly fictional. Under no circumstances can Pork tokens or Porky Mart capital be exchanged, bartered, or wire-transferred out of the software container into real-world fiat currencies or tangible agricultural commodities.

---

## 🎨 User Interface & Particle Engine Controls

To support smooth particle movement without relying on heavy third-party gaming engines, the system utilizes a layered Tkinter `Canvas` element stretched across relative width and height constraints.

* **Particle Cascading Engine:** Interaction with the central pig or high-tier automation components triggers the generation of falling mini-pig elements at randomized horizontal points above the window view.
* **Layer Order Management:** Every newly spawned asset is automatically forced to the bottom of the visual stack using canvas tag ordering (`tag_lower`). This keeps falling particles floating behind your shop buttons and scoreboard values.
* **Hardware Throttling Protections:** To protect system hardware from performance drops due to graphical object inflation, the engine enforces a strict cap of **250 simultaneous active falling objects**. Any generation requests exceeding this cap are dropped until old elements fall out of bounds and are cleared from memory.

---

## 🛠️ Binary Compilation & Build Protocols

When compiling Python source directories into standalone single-executable formats via automation scripts like `[yinstall.py`, compilation can run into permission blocks.

### Overcoming the `WinError 5` Permission Lock

```text
PermissionError: [WinError 5] Access is denied: '...\Porkade.exe'

```

This error is a security enforcement action taken directly by the host operating system's kernel. It occurs when PyInstaller tries to overwrite an existing target binary that is currently locked. To resolve this, check for the three primary causes:

1. **Dangling Background Processes:** A previous test version of the file is still active as a hidden thread. Kill it via Windows Task Manager.
2. **File Explorer Locks:** A local File Explorer window has the distribution folder open and is locking the file to render its custom `Bird.ico` asset. Close the directory and rebuild.
3. **Antivirus Scanning Interference:** Real-time scanning tools may briefly lock down newly generated binary streams to evaluate threat payloads. Temporarily whitelist your build directory.

### Distribution Separation Workaround

To avoid these system conflicts, configure your compiler configurations to route builds explicitly into a clean, separated folder layout using the `--distpath` flag:

```bash
pyinstaller --clean --onefile --windowed --icon=assets/Bird.ico --distpath ./dist/Porkade Porkade.py

```

---

## ⚖️ Terms & Conditions of Porcine Management

### 1. Warranty Disclaimer

The entire software ecosystem is provided strictly **"as-is"** and **"as-available"**, without warranties or guarantees of any kind, either expressed or implied. The developer does not guarantee that your high scores will save perfectly across unexpected system shutdowns, or that passive generation loops will run at an exact millisecond interval on older systems.

### 2. Liability Limits

To the maximum extent permitted by local law, the developer shall not be held liable for any system lag, lost save configurations, keyboard wear-and-tear from rapid clicking, or drops in daily workplace productivity caused by an addiction to building a virtual pork empire.

### 3. Agreement Termination

You may terminate this usage agreement at any time by closing all running game windows, ending related background tasks, and completely purging the game directory from your storage systems. The developer reserves the right to update asset balances, tweak item pricing, adjust inflation rates, or alter UI layouts at any time without prior notice.

---

```text
========================================================================
             [ END OF TERMS AND CONDITIONS DOCUMENTATION ]
               INSERT VIRTUAL COIN TO CONTINUE OPERATION
========================================================================

```
