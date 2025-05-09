import typer
import subprocess
import os
import requests
from sharded import __version__ as v
from sharded.CLI import addons
from rich import print
from typing_extensions import Annotated, Optional


app = typer.Typer()
app.add_typer(
    addons.app,
    name="addons",
    rich_help_panel="Dedicated Menus",
)
app._add_completion = False

user_dir = os.path.expanduser("~")
addons_dir = os.path.join(user_dir, ".sharded", "addons")


@app.callback()
def callback(version: Annotated[Optional[bool], typer.Option("--version", "-v", help="Showcases the sharded version")] = False):
    """
    Sharded CLI - Managing your instance of Sharded Runtime and devtools.\n
    Docs: https://docs.sharded.app/
    """
    os.makedirs(addons_dir, exist_ok=True)
    if version:
        print(f"[dim]Sharded {v}[/dim]")


@app.command()
def start():
    """
    Launches a running instance of Sharded Runtime.
    """
    subprocess.run(["python", "-m", "sharded.main"], check=True, shell=False)

@app.command()
def update():
    """
    Updates the Sharded package to the latest version.
    """
    try:
        try:
            response = requests.get("https://pypi.org/pypi/sharded/json")
            latest_version = response.json()["info"]["version"]
            print(f"[dim]Latest version: {latest_version}[/dim]")

            if v == latest_version:
                print("[yellow]You already have the latest version.[/yellow]")
                return
            
            confirm = typer.confirm(f"Update from {v} to {latest_version}?")
            if not confirm:
                print("[yellow]Update cancelled.[/yellow]")
                return
            
        except Exception as e:
            print(f"[yellow]Could not check latest version: {e}[/yellow]")
            confirm = typer.confirm("Do you want to continue with the update?")
            if not confirm:
                print("[yellow]Update cancelled.[/yellow]")
                return
            
        subprocess.run(["pip", "install", "--upgrade", "sharded"], check=True)
        print("[green]Sharded updated successfully! ✨")
    except subprocess.CalledProcessError:
        print("[red]Failed to update Sharded. Please try again with administrator privileges.")