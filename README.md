# breach

```
██████╗ ██████╗ ███████╗ █████╗  ██████╗██╗  ██╗
██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║
██████╔╝██████╔╝█████╗  ███████║██║     ███████║
██╔══██╗██╔══██╗██╔══╝  ██╔══██║██║     ██╔══██║
██████╔╝██║  ██║███████╗██║  ██║╚██████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
```

> A terminal-based SCP Foundation database viewer. Access classified files directly from your command line.

---

## Features

- 🔍 **Lookup any SCP** by number directly from the SCP Wiki
- 🎲 **Random SCP** — optionally filtered by object class
- 🔴 **Color-coded by class** — Safe, Euclid, Keter, Thaumiel, Apollyon
- ⚠️ **Dramatic warnings** for dangerous object classes
- 🔐 **Clearance Level system** — set your access level and watch restricted SCPs get censored
- ⬛ **Real redactions preserved** — `█████` from the original articles stay intact
- ⭐ **Favorites** — save SCPs with personal notes
- 📜 **History** — track your access log
- 💾 **Local cache** — fetched SCPs are stored locally to avoid repeated requests

---

## Installation

```bash
git clone https://github.com/matheusc457/breach
cd breach
pip install -e .
```

---

## Usage

```bash
# Look up a specific SCP
breach get 173

# Random SCP
breach random

# Random SCP filtered by class
breach random keter

# Save to favorites while fetching
breach get 049 --save --note "The Plague Doctor"

# Manage favorites
breach favorites list
breach favorites add 682
breach favorites remove 682

# View access history
breach history show
breach history clear

# Set your clearance level (1–5)
breach config --level 3
breach config --show
```

---

## Clearance Levels

| Level | Access |
|-------|--------|
| 1     | Safe class only |
| 2     | Safe + Euclid |
| 3     | + Keter |
| 4     | + Thaumiel / Archon |
| 5     | Full access (default) |

SCPs above your clearance level will appear heavily ████████ censored.

---

## Object Class Colors

| Class       | Color  |
|-------------|--------|
| Safe        | 🟢 Green |
| Euclid      | 🟡 Yellow |
| Keter       | 🔴 Red |
| Thaumiel    | 🟣 Magenta |
| Apollyon    | ⚫ Dark Red |
| Neutralized | ⬜ Gray |

---

## Disclaimer

This project is a fan-made tool. All SCP content belongs to the [SCP Wiki](https://scp-wiki.wikidot.com/) and is licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).

