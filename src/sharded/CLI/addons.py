import typer
import os
import requests
import json
from pathlib import Path
from typing_extensions import Annotated, Optional
from rich import print
from rich.panel import Panel
from rich.progress import Progress

app = typer.Typer()

user_dir = os.path.expanduser("~")
addons_dir = os.path.join(user_dir, ".sharded", "addons")


@app.callback()
def callback():
    """
    Sharded Addon(s) Manager\n
    View extended docs at: https://sharded.app/addons
    """


@app.command()
def view():
    """
    View currently installed addons and update them.
    """
    if not os.listdir(addons_dir):
        print(
            Panel(
                "No addons detected.\nLearn more about addons here: https://sharded.app/addons",
                title="Addons Manager",
            )
        )
    else:
        for addon in os.listdir(addons_dir):
            addons_info = []
            for addon in os.listdir(addons_dir):
                addon_path = os.path.join(addons_dir, addon)
                metadata_path = os.path.join(addon_path, "metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                        addons_info.append(
                            f"[bold cyan]{metadata.get('name', 'Unknown')}[/bold cyan] by [bold]{metadata.get('author', 'Unknown')}[/bold] [dim]- {metadata.get('version', 'Unknown')}[/dim]"
                        )
                    except json.JSONDecodeError:
                        addons_info.append(
                            f"[bold red]{addon}[/bold red]\n"
                            "Failed to parse metadata.json. The file might be corrupted."
                        )
                else:
                    addons_info.append(
                        f"[bold red]{addon}[/bold red]\n"
                        "Missing metadata.json. The addon might be incomplete."
                    )
            print(
                Panel(
                    "\n\n".join(addons_info),
                    title="Installed Addons",
                    border_style="green",
                )
            )


@app.command()
def install(
    addon: Annotated[
        str,
        typer.Argument(
            help="Addon's author and name. (shardedinteractive/addon_example)"
        ),
    ] = None,
    local: Annotated[
        Optional[Path],
        typer.Option(
            help="If developing an addon or is a private addon, use this flag and the path to the addon."
        ),
    ] = None,
):
    """
    Installs a new addon or updates an existing one.
    """
    if local is None and addon is not None:
        try:
            metadata_url = (
                f"https://raw.githubusercontent.com/{addon}/main/metadata.json"
            )

            response = requests.get(metadata_url)
            response.raise_for_status()

            metadata = response.json()

            print(
                Panel(
                    f"[bold cyan]{metadata.get('name', 'Unknown')}[/bold cyan] [dim]- {metadata.get('version', 'Unknown')}[/dim]\n"
                    f"{metadata.get('description', 'No description provided.')}\n"
                    f"\nMaintained by [bold]{metadata.get('author', 'Unknown')}[/bold] [dim]using manifest v{metadata.get('manifest_version', '???')} of Sharded.",
                    title="Addon Metadata",
                    border_style="blue",
                    title_align="left"
                )
            )
            confirmation = typer.confirm("Are you sure you want to install this addon?")
            if confirmation:
                addon_dir = os.path.join(addons_dir, metadata["name"])
                os.makedirs(addon_dir, exist_ok=True)

                with Progress() as progress:
                    task = progress.add_task("[cyan]Downloading addon...", total=2)

                    metadata_path = os.path.join(addon_dir, "metadata.json")
                    with open(metadata_path, "w") as f:
                        json.dump(metadata, f, indent=4)
                    progress.update(task, advance=1)

                    addon_files_url = f"https://api.github.com/repos/{addon}/contents/"
                    response = requests.get(addon_files_url)
                    response.raise_for_status()
                    files = response.json()
                    for file in files:
                        if file["type"] == "dir" and file["name"] == "addon":
                            addon_url = file["url"]
                            addon_dir_path = os.path.join(addon_dir, file["name"])
                            os.makedirs(addon_dir_path, exist_ok=True)

                            addon_files_response = requests.get(addon_url)
                            addon_files_response.raise_for_status()
                            addon_files = addon_files_response.json()

                            for addon_file in addon_files:
                                if addon_file["type"] == "file":
                                    file_url = addon_file["download_url"]
                                    file_path = os.path.join(addon_dir_path, addon_file["name"])
                                    file_response = requests.get(file_url)
                                    file_response.raise_for_status()

                                    with open(file_path, "wb") as f:
                                        f.write(file_response.content)

                    progress.update(task, advance=1)

                print(
                    f"[green]Addon '{metadata['name']}' installed successfully![/green]"
                )
            else:
                print("[red]Addon installation canceled.[/red]")
        except requests.exceptions.RequestException as e:
            print(f"[red]{e}[/red]")
        except json.JSONDecodeError:
            print(
                "[red]Failed to parse metadata.json. Ensure the file is valid JSON.[/red]"
            )
    else:
        print(f"Installing from local path: {local}")


if __name__ == "__main__":
    app()
