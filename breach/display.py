import re
import random
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.rule import Rule
from rich import box

console = Console()

CLASS_COLORS = {
    "safe":        "bright_green",
    "euclid":      "yellow",
    "keter":       "bright_red",
    "thaumiel":    "bright_magenta",
    "apollyon":    "red",
    "archon":      "dark_orange",
    "neutralized": "bright_black",
    "pending":     "cyan",
    "explained":   "bright_cyan",
}

REDACTED_CHANCE = 0.0  # real redactions preserved; no extra random censorship by default


def _class_color(obj_class: str) -> str:
    return CLASS_COLORS.get(obj_class.lower(), "white")


def _censor_text(text: str, level: int, required: int) -> str:
    """If clearance is insufficient, censor most of the text."""
    if level >= required:
        return text
    words = text.split()
    censored = []
    for word in words:
        if random.random() < 0.85:
            censored.append("█" * len(word))
        else:
            censored.append(word)
    return " ".join(censored)


def print_warning(obj_class: str):
    color = _class_color(obj_class)
    warning = Text()
    warning.append("⚠  WARNING  ⚠\n", style=f"bold {color}")
    warning.append(f"Object Class {obj_class.upper()} entity detected.\n", style=f"bold {color}")
    warning.append("Proceed with extreme caution. Unauthorized access is a capital offense.", style=color)
    console.print(Panel(warning, border_style=color, expand=False))
    console.print()


def print_access_denied(number: int, required: int, user_level: int):
    msg = Text()
    msg.append("ACCESS DENIED\n", style="bold bright_red")
    msg.append(f"\nSCP-{number:03d} requires ", style="white")
    msg.append(f"Clearance Level {required}", style="bold bright_red")
    msg.append(f"\nYour current level: ", style="white")
    msg.append(f"Level {user_level}\n", style="bold yellow")
    msg.append("\n██████████████████████████████\n", style="bright_red")
    msg.append("██  CLASSIFIED  ██  CLASSIFIED  ██\n", style="bright_red")
    msg.append("██████████████████████████████", style="bright_red")
    console.print(Panel(msg, title="[bold red]⛔ FOUNDATION SECURITY SYSTEM[/]", border_style="bright_red"))


def print_scp(data: dict, user_level: int):
    number      = data["number"]
    title       = data["title"]
    obj_class   = data["object_class"]
    containment = data.get("containment") or "[italic]REDACTED[/italic]"
    description = data.get("description") or "[italic]REDACTED[/italic]"
    required    = data.get("clearance_required", 3)
    color       = _class_color(obj_class)

    # Warning banner for dangerous classes
    if data.get("is_warning"):
        print_warning(obj_class)

    # Censor if below clearance
    if user_level < required:
        containment = _censor_text(containment, user_level, required)
        description = _censor_text(description, user_level, required)

    # Header
    header = Text()
    header.append(f"Item #: SCP-{number:03d}", style="bold white")
    if title and f"SCP-{number:03d}" not in title:
        header.append(f"  —  {title}", style="dim white")

    # Object class badge
    class_badge = Text()
    class_badge.append("Object Class: ", style="white")
    class_badge.append(f" {obj_class.upper()} ", style=f"bold reverse {color}")

    # Clearance indicator
    lock = "🔓" if user_level >= required else "🔒"
    class_badge.append(f"   {lock} Clearance Level {required} Required", style="dim")

    # Containment section
    cont_title  = Text("◼ SPECIAL CONTAINMENT PROCEDURES", style="bold white")
    desc_title  = Text("◼ DESCRIPTION", style="bold white")

    body = Text()
    body.append_text(cont_title)
    body.append("\n\n")
    body.append(containment)
    body.append("\n\n")
    body.append_text(desc_title)
    body.append("\n\n")
    body.append(description)

    panel = Panel(
        body,
        title=header,
        subtitle=class_badge,
        border_style=color,
        padding=(1, 2),
    )

    # Tags line
    tag_line = Text("\n  Tags: ", style="dim")
    if data.get("tags"):
        for tag in data["tags"]:
            tag_line.append(f"[{tag}] ", style="dim cyan")

    source_line = f"\n  [dim]Source: {data['url']}[/dim]\n"

    # Use pager for long content
    desc = data.get("description") or ""
    use_pager = len(desc) > 3000

    if use_pager:
        with console.pager(styles=True):
            console.print(panel)
            console.print(tag_line)
            console.print(source_line)
    else:
        console.print(panel)
        console.print(tag_line)
        console.print(source_line)


def print_favorites(favorites: list):
    if not favorites:
        console.print("[yellow]No favorites saved yet. Use `breach get <number> --save` to add one.[/yellow]")
        return

    table = Table(title="⭐ Saved Favorites", box=box.SIMPLE_HEAVY, border_style="yellow")
    table.add_column("SCP #",    style="bold white", width=8)
    table.add_column("Title",    style="white")
    table.add_column("Class",    style="bold")
    table.add_column("Note",     style="dim italic")
    table.add_column("Saved",    style="dim")

    for fav in favorites:
        obj_class = fav.get("object_class") or "Unknown"
        color     = _class_color(obj_class)
        table.add_row(
            f"SCP-{fav['number']:03d}",
            fav["title"],
            f"[{color}]{obj_class.upper()}[/{color}]",
            fav.get("note") or "—",
            fav["saved_at"][:10],
        )

    console.print(table)


def print_history(history: list):
    if not history:
        console.print("[yellow]No history yet.[/yellow]")
        return

    table = Table(title="📜 Access History", box=box.SIMPLE_HEAVY, border_style="bright_black")
    table.add_column("SCP #",    style="bold white", width=8)
    table.add_column("Title",    style="white")
    table.add_column("Accessed", style="dim")

    for entry in history:
        table.add_row(
            f"SCP-{entry['number']:03d}",
            entry["title"],
            entry["accessed_at"][:16].replace("T", " "),
        )

    console.print(table)


def print_error(msg: str):
    console.print(f"[bold red]ERROR:[/bold red] {msg}")


def print_success(msg: str):
    console.print(f"[bold green]✔[/bold green] {msg}")


def print_info(msg: str):
    console.print(f"[bold cyan]ℹ[/bold cyan]  {msg}")

