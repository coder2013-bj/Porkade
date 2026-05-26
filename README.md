These two apps are currently in development. 
Angry pork, even more so. Please do not copy them to other devices without my consent. Feel free to play them, and have a look at the code in the folders. Please do not edit the code though. 

Thanks,
Barney Jack


CC-BY-ND



# 🐷 THE PORKADE ECOSYSTEM: TERMS AND CONDITIONS OF USE, RECREATION, AND PORCINE MANAGEMENT

**Document Version:** 2.4.0-2026

**Effective Date:** May 22, 2026

**Applicability:** Universal across all components, binaries, scripts, and save architecture within the Porkade suite.

---

## PREAMBLE & BINDING AGREEMENT

Please read this extraordinarily comprehensive document with absolute care before executing any operational parameters within this ecosystem. By double-clicking `Porkade.exe`, launching `Porkade.py` through an Integrated Development Environment (IDE) such as Thonny, building binary payloads via PyInstaller wrappers like `[yinstall.py`, or clicking upon the nose of any digital swines, you are hereby entering into a legally binding, recreationally absolute, and structurally permanent contract with the **Porkade Development, Farming, and Retail Management Consortium**.

If you do not agree to be bound by every single clause, sub-clause, note, and humorously long technical restriction outlined below, you are strictly prohibited from entering the Porkade. In such an event, your only recourse is to close your active Tkinter main loop threads immediately, delete any local configuration trees, and completely purge your system registry of all pork-related data points.

---

## SECTION 1: ARCHITECTURE, ENGINE DEPLOYMENT, AND LOCAL FILESYSTEM DECOUPLING

### 1.1 The Master Control Deck (`Porkade.py`)

The user interface known colloquially as the **Porkade** acts exclusively as an administrative hub and master orchestration dashboard. It does not natively execute the calculations for item production, asset inflation, or customer queuing loops; rather, it functions by mapping contextual actions to independent execution pathways through systemic subfolder calls.

### 1.2 Path Inversion & Absolute Directory Containment

To guarantee that sub-assets (including but not limited to custom icon configurations, bitmap structures, visual frames, and localized storage files) resolve perfectly across fluctuating local runtime platforms, the software architecture operates on a strict directory safety wrapper.

* **Frozen State Operational Matrix:** When compiled into standalone binary payloads, the game scripts utilize `sys.executable` discovery hooks to locate their exact physical placement on the host machine's solid-state or hard-disk drives.
* **Scripted Execution Matrix:** When running as a loose script through an IDE, the system tracks runtime positions dynamically via system arguments (`sys.argv[0]`) or absolute global paths (`__file__`) to isolate assets directly inside the folder where the execution command originated, rather than defaulting blindly to the operating system's standard user directories.

### 1.3 Subprocess Isolation & Working Directory (`cwd`) Compliance

When launching secondary computational modules—such as *Flappy Pork*, *Angry Pork*, *Crossy Pork*, *Pork Clicker*, or *Porky Mart*—the launcher explicitly instantiates a separate process thread. All calls initiated via Python's underlying `subprocess.Popen` array require the strict declaration of a Current Working Directory (`cwd`) parameter pointing exactly to the specific child module's workspace folder.

This parameters-driven encapsulation guarantees that child processes look for their respective assets (e.g., `pig_sprite.png`, `Bird.ico`) inside their own local folders instead of searching inside the parent suite's primary root directories.

---

## SECTION 2: DIGITAL ASSET REGISTRATION, FILE CORRUPTION, AND SAVE STATE MANIPULATION

### 2.1 Local Object Notation (.json) Infrastructure

Progress data is maintained completely locally through structured JavaScript Object Notation (`.json`) files. The infrastructure relies entirely on the successful generation and reading of these files (specifically `save_data.json` for clicker games and `mart_save.json` for commercial tycoons) within the local workspace environment.

### 2.2 Schema Definitions and Parameter Parsing

The local save file operates under a hardcoded structural schema. When the game triggers its auto-save state serialization, it parses exact variable keys into the data payload. The parameters managed include:

* **Pork Accumulation Value (`pork_count`):** A representation of the player's total current balance.
* **Passive Generation Capacity (`pork_per_second`):** The aggregate passive generation tick rate.
* **Click Multiplication Level (`pork_per_click`):** The quantitative payout value of manual interface interactions.
* **Inflationary Procurement Cost Matrices:** Variables tracking the increasing costs of assets, specifically `feeder_cost`, `farm_cost`, `mud_cost`, `factory_cost`, and `shed_cost`.
* **Structural Asset Ownership Registries:** Counts of active assets on the map, including `feeder_count`, `farm_count`, `mud_count`, `factory_count`, and `shed_count`.

### 2.3 The Reset Paradox & Directory Displacement Disclaimer

Users frequently observe that deleting a localized `save_data.json` file fails to execute a true structural wipe of their historical scores and active property assets. This paradox is caused by system directory displacement.

If a compiled application or script is executed from an improperly mapped development terminal, the host machine may generate the real save configuration file inside an alternative path entirely (such as Thonny's installation tree or the primary system profile folder).

The user explicitly agrees that searching for hours for a misplaced file is a systemic issue with local pathing, and they absolve the software from any data discrepancies arising from manual filesystem intervention.

### 2.4 Force-Overwriting through System Interception

To execute a hard reset of progress when normal file deletion fails, the user is authorized to perform a manual script intercept using the following modification sequence:

1. Locate the game's core instance initialization method (`__init__`).
2. Place a comment block indicator (`#`) before the execution line assigned to pull existing save files from disk (`self.load_game()`).
3. Add a temporary direct data serialization command immediately underneath it (`self.save_game()`).
4. Run the code exactly once to force a clean, uninflated save file directly onto the true active file path, clearing out previous progression records.
5. Revert the code back to its original structural form by restoring the loading routines and removing the temporary forced saving block.

---

## SECTION 3: IN-GAME FISCAL POLICIES, VIRTUAL INFLATION, AND ASSET ACQUISITION

### 3.1 Absolute Invalidation of Real-World Value

All currencies, financial assets, points, materials, and livestock options generated across the software suite are strictly fictional.

* Under no circumstances can **Pork** tokens be transferred, exchanged, bartered, or wire-transferred out of the software container into fiat currencies (including but not limited to USD, EUR, GBP, or CAD).
* **Porky Mart** capital, warehouse stock allocations, and shop revenue generated from virtual transactions cannot be redeemed for physical food products, agricultural commodities, or retail merchandise.
* Any attempt to pay for real-world municipal utilities, digital streaming subscriptions, or tangible commercial items using automated pork farming points will be viewed as a breach of reality and may result in confusion or store eviction.

### 3.2 Inflation Coefficient Logic & Asset Tiers

The economic model of the software uses exponential inflation coefficients to simulate late-stage resource scaling. Every time an asset is bought, its base cost updates dynamically by calculating the current base purchase price multiplied by a specific asset inflation factor.

```
                [ New Cost = Integer ( Current Cost * Inflation Factor ) ]

```

| Asset ID | Base Unit Cost | Production Value | Compounding Inflation Factor |
| --- | --- | --- | --- |
| **Auto-Feeder** | 15 Pork | +1 Pork / Second | 1.3x Compound Rate |
| **Golden Mud** | 50 Pork | +1 Pork / Click | 1.5x Compound Rate |
| **Shed Structure** | 75 Pork | +4 Pork / Click | 1.4x Compound Rate |
| **Pig Farm** | 100 Pork | +8 Pork / Second | 1.4x Compound Rate |
| **Factory Farm** | 150 Pork | +12 Pork / Second | 1.4x Compound Rate |

The system uses basic truncation logic (`int()`) to drop all remaining floating-point decimals from the newly generated cost integer, preventing fractional tokens from corrupting your save files.

---

## SECTION 4: USER INTERFACE ANIMATION MATRIX & FULL-WINDOW CANVAS LIMITATIONS

### 4.1 Layered Graphics Constraints via Tkinter Canvas

To support smooth particle movement without relying on heavy third-party gaming frameworks, the updated versions of the software use a layered Tkinter `Canvas` element. This canvas is stretched across the UI using relative width and height constraints to scale perfectly with the window.

The user understands that all texts, status headers, shop buttons, and interactive hitboxes are drawn directly onto this single canvas or attached via specific window coordinate hooks.

### 4.2 Particle Cascading and Hardware Throttling

The game suite includes an automated cascading particle engine that handles visual objects moving down the screen.

* **Spawn Density Regulations:** When the player interacts with the central pig or when high-tier passive automation upgrades produce a resource tick, the system generates falling mini-pig elements at randomized horizontal positions above the window view.
* **Layer Order Management:** Every newly spawned asset is automatically forced to the bottom of the visual stack using canvas tag ordering (`tag_lower`). This keeps the falling particles floating behind your shop buttons and scoreboard values so they don't block important gameplay information.
* **System Resource Limits:** To protect your computer's hardware from performance issues caused by creating too many graphical items at once, the engine enforces a strict cap of **250 simultaneous active falling objects**. Any generation request that goes over this cap is dropped until old elements fall completely out of bounds and are cleared from memory.

---

## SECTION 5: PYINSTALLER BUILD PROTOCOLS, WINDOWS LOCK ENFORCEMENTS, AND SYSTEM COMPILATION ERRORS

### 5.1 Binary Compilation and the WinError 5 Permission Lock

When compiling python source directories into single-executable standalone formats via specialized automation scripts like `[yinstall.py`, the user must be prepared to handle basic file lock errors. The common error message:

```text
PermissionError: [WinError 5] Access is denied: '...\Porkade.exe'

```

is a security enforcement action taken directly by the host operating system's kernel. This lock occurs when PyInstaller tries to replace an existing target executable file name that is locked or restricted by active system operations.

### 5.2 Causes of Application Locks

The user acknowledges that an application block typically happens due to three main causes:

1. **Background Processes:** A previous test version of the file is still running as a hidden background thread in the Windows Task Manager.
2. **File Explorer Locks:** A local File Explorer window has the distribution folder open and is actively using the file to show its custom `Bird.ico` icon asset.
3. **Antivirus Scanning:** Local antivirus software or Windows Defender real-time scanning tools lock down the newly compiled binary file to check it for threats, preventing PyInstaller from completing its build routine.

### 5.3 Distribution Separation Workaround

To systematically avoid these permission issues, the compiler configurations must be updated to route files into a separate, clean folder layout.

* The script building system uses a dedicated output parameter (`--distpath`) pointing to a standalone distribution subfolder (`...\Porkade\dist`).
* Keeping your active development files separate from your finalized program folders ensures that PyInstaller can always write new binary files without running into file conflicts with your operating system.

---

## SECTION 6: DISCLAIMERS, LIABILITY LIMITS, AND TERMINATION PROTOCOLS

### 6.1 Warranty Disclaimer

The entire software ecosystem is provided strictly "as-is" and "as-available," without warranties or guarantees of any kind, either expressed or implied. The developer does not guarantee that your high scores will be saved perfectly, that the pig button will scale perfectly with every display resolution, or that the passive generation loops will run at an exact millisecond interval on older systems.

### 6.2 Liability Limits

To the maximum extent permitted by local law, the developer shall not be held liable for any system lag, lost data files, corrupted save documents, keyboard wear-and-tear from clicking too fast, or drops in daily productivity caused by an addiction to building a virtual pork empire.

### 6.3 Agreement Termination

This agreement remains fully active until it is terminated by either party. The user can terminate this contract at any time by closing all running game windows, ending all related background tasks, and completely deleting the primary game folder from their storage drives.

The developer reserves the right to update upgrade balancing, tweak item pricing, adjust inflation rates, or change button colors whenever they want without providing prior notice.

---

## SECTION 7: EXPLICIT ACKNOWLEDGMENT & COMPLIANCE

By continuing to run the software application, configuring local resource dependencies, or clicking the central interactive buttons, you certify that you have read, understood, and agreed to every section of these Terms and Conditions. You are now officially cleared to insert a digital coin and enter the arcade.

```text
========================================================================
             [ END OF TERMS AND CONDITIONS DOCUMENTATION ]
               INSERT VIRTUAL COIN TO CONTINUE OPERATION
========================================================================

```
