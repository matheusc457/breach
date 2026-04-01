# breach

```
██████╗ ██████╗ ███████╗ █████╗  ██████╗██╗  ██╗
██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║
██████╔╝██████╔╝█████╗  ███████║██║     ███████║
██╔══██╗██╔══██╗██╔══╝  ██╔══██║██║     ██╔══██║
██████╔╝██║  ██║███████╗██║  ██║╚██████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
```

> Access classified Foundation files directly from your terminal.

---

## Features

- Fetches live data directly from the [SCP Wiki](https://scp-wiki.wikidot.com)
- Color-coded output by object class
- Original `████` redactions preserved from source articles
- Clearance Level system — entries above your level appear censored
- Dramatic warnings for Keter and Apollyon class entities
- Pagination for long entries
- Local cache to avoid repeated requests
- Favorites with personal notes
- Access history log

---

## Requirements

- Python 3.10+
- [pipx](https://pipx.pypa.io) (recommended) or pip

---

## Installation

```bash
git clone https://github.com/matheusc457/breach
cd breach
pipx install .
```

That's it. The `breach` command is now available globally.

### Alternative (virtual environment)

```bash
python -m venv .venv && source .venv/bin/activate
pip install .
```

---

## Usage

### Look up a SCP
```bash
breach get 173
breach get 682
```

### Random SCP
```bash
breach random
breach random keter
breach random euclid
```

### Favorites
```bash
breach get 049 --save --note "The Plague Doctor"
breach favorites list
breach favorites add 173
breach favorites remove 173
```

### History
```bash
breach history show
breach history clear
```

### Clearance Level
```bash
breach config --level 3   # restrict access
breach config --level 5   # full access (default)
breach config --show
```

---

## Object Classes

| Class | Color |
|---|---|
| Safe | 🟢 Green |
| Euclid | 🟡 Yellow |
| Keter | 🔴 Red |
| Thaumiel | 🟣 Magenta |
| Apollyon | ⚫ Dark Red |
| Neutralized | ⬜ Gray |

---

## Clearance Levels

| Level | Access |
|---|---|
| 1 | Safe only |
| 2 | Safe + Euclid |
| 3 | + Keter |
| 4 | + Thaumiel / Archon |
| 5 | Full access (default) |

SCPs above your level will appear heavily ████████ censored.

---

## Uninstall

```bash
pipx uninstall breach
rm -rf ~/.breach   # removes cache, favorites and history
```

---

## Disclaimer

All SCP content belongs to the [SCP Wiki](https://scp-wiki.wikidot.com) and is licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). This project is not affiliated with the SCP Foundation.
