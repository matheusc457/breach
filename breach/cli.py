import click
from . import database as db
from . import scraper
from . import display as ui


def _get_level() -> int:
    return int(db.config_get("clearance_level") or 5)


@click.group()
def cli():
    """
    \b
    ██████╗ ██████╗ ███████╗ █████╗  ██████╗██╗  ██╗
    ██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║
    ██████╔╝██████╔╝█████╗  ███████║██║     ███████║
    ██╔══██╗██╔══██╗██╔══╝  ██╔══██║██║     ██╔══██║
    ██████╔╝██║  ██║███████╗██║  ██║╚██████╗██║  ██║
    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝

    SCP Foundation Terminal — Access classified files.
    """
    db.init_db()


# ── breach get ─────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("number", type=int)
@click.option("--save", "-s", is_flag=True, help="Save to favorites.")
@click.option("--note", "-n", default="", help="Note to attach when saving.")
@click.option("--no-cache", is_flag=True, help="Force fetch from wiki, ignore cache.")
def get(number: int, save: bool, note: str, no_cache: bool):
    """Retrieve an SCP entry by number.\n\nExample: breach get 173"""

    user_level = _get_level()

    # Try cache first
    data = None
    if not no_cache:
        data = db.cache_get(number)

    if data is None:
        ui.console.print(f"[dim]Fetching SCP-{number:03d} from the Foundation database...[/dim]")
        data = scraper.fetch_scp(number)

        if data is None:
            ui.print_error(f"SCP-{number:03d} not found. It may not exist or the wiki is unreachable.")
            return

        db.cache_set(number, data)

    # Check clearance
    required = data.get("clearance_required", 3)
    if user_level < required:
        ui.print_access_denied(number, required, user_level)
        return

    # Display
    ui.print_scp(data, user_level)

    # Log history
    db.history_add(number, data["title"])

    # Save to favorites
    if save:
        db.favorite_add(number, data["title"], data["object_class"], note)
        ui.print_success(f"SCP-{number:03d} saved to favorites.")


# ── breach random ──────────────────────────────────────────────────────────────

@cli.command()
@click.argument("object_class", required=False, default=None)
@click.option("--save", "-s", is_flag=True, help="Save to favorites.")
def random(object_class: str | None, save: bool):
    """Retrieve a random SCP entry.\n\nOptionally filter by class: breach random keter"""

    user_level = _get_level()

    ui.console.print("[dim]Accessing random file from the Foundation database...[/dim]")

    data = scraper.fetch_random(object_class)

    if data is None:
        msg = f"Could not find a random SCP"
        if object_class:
            msg += f" with class '{object_class}'"
        ui.print_error(msg + ". Try again.")
        return

    db.cache_set(data["number"], data)

    required = data.get("clearance_required", 3)
    if user_level < required:
        ui.print_access_denied(data["number"], required, user_level)
        return

    ui.print_scp(data, user_level)
    db.history_add(data["number"], data["title"])

    if save:
        db.favorite_add(data["number"], data["title"], data["object_class"])
        ui.print_success(f"SCP-{data['number']:03d} saved to favorites.")


# ── breach favorites ───────────────────────────────────────────────────────────

@cli.group()
def favorites():
    """Manage your saved SCP entries."""
    pass


@favorites.command("list")
def favorites_list():
    """List all saved favorites."""
    favs = db.favorite_get_all()
    ui.print_favorites(favs)


@favorites.command("add")
@click.argument("number", type=int)
@click.option("--note", "-n", default="", help="Personal note.")
def favorites_add(number: int, note: str):
    """Add an SCP to favorites by number."""
    data = db.cache_get(number)
    if data is None:
        ui.console.print(f"[dim]Fetching SCP-{number:03d}...[/dim]")
        data = scraper.fetch_scp(number)
        if data is None:
            ui.print_error(f"SCP-{number:03d} not found.")
            return
        db.cache_set(number, data)

    db.favorite_add(number, data["title"], data["object_class"], note)
    ui.print_success(f"SCP-{number:03d} added to favorites.")


@favorites.command("remove")
@click.argument("number", type=int)
def favorites_remove(number: int):
    """Remove an SCP from favorites."""
    if not db.favorite_exists(number):
        ui.print_error(f"SCP-{number:03d} is not in your favorites.")
        return
    db.favorite_remove(number)
    ui.print_success(f"SCP-{number:03d} removed from favorites.")


# ── breach history ─────────────────────────────────────────────────────────────

@cli.group()
def history():
    """View or clear your access history."""
    pass


@history.command("show")
@click.option("--limit", "-l", default=20, help="Number of entries to show.")
def history_show(limit: int):
    """Show recent access history."""
    entries = db.history_get(limit)
    ui.print_history(entries)


@history.command("clear")
def history_clear():
    """Clear all access history."""
    db.history_clear()
    ui.print_success("History cleared.")


# ── breach config ──────────────────────────────────────────────────────────────

@cli.command()
@click.option("--level", "-l", type=click.IntRange(1, 5), help="Set your clearance level (1–5).")
@click.option("--show", is_flag=True, help="Show current configuration.")
def config(level: int | None, show: bool):
    """Configure your Foundation terminal access settings."""

    if show or (level is None):
        current_level = _get_level()
        ui.print_info(f"Current clearance level: [bold yellow]Level {current_level}[/bold yellow]")
        ui.console.print("""
  [dim]Clearance levels:[/dim]
  [dim]  Level 1 — Safe class only[/dim]
  [dim]  Level 2 — Safe + Euclid[/dim]
  [dim]  Level 3 — + Keter[/dim]
  [dim]  Level 4 — + Thaumiel / Archon[/dim]
  [dim]  Level 5 — Full access (default)[/dim]
""")
        return

    db.config_set("clearance_level", str(level))
    ui.print_success(f"Clearance level set to [bold yellow]Level {level}[/bold yellow].")


def main():
    cli()


if __name__ == "__main__":
    main()
