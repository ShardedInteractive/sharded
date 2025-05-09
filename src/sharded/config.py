import logging
import os
import configparser
import requests
from dotenv import load_dotenv
from rich.progress import (
    Progress,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)
from rich.panel import Panel
from rich.console import Console

log = logging.getLogger("discord")


class Environment:
    """`Environment` is a class that provides a way to dynamically or statically load environment variables from a `.env` file."""

    def __init__(self, data: dict = None):
        load_dotenv()
        self._data = data or {
            "DISCORD_TOKEN": os.getenv("DISCORD_TOKEN"),
            "GUILD_ID": os.getenv("GUILD_ID"),
            "SERVICE_KEY": os.getenv("SERVICE_KEY"),
        }

    def __getitem__(self, key: str):
        return self._data[key]

    def vital(self, key: str = None, provider: str = None) -> str | dict | None:
        """vital is a method that provides a way to dynamically or statically load important environment variables from a `.env` file.

        Args:
            key (str): The value in which you want to receive from the environment. (Can be optional if `dynamic` is the provider.)
            provider (str): `static` will only get you the requested environmental variable. `dynamic` will give you access to a database for easier access to environmental variables. Defaults to `static`.

        Returns:
            str: The value of the environmental variable requested.
            dict: If `provider` is set to `dynamic`, a dictionary will be returned with all the environmental variables loaded into a temporary database.
            None: If the key is not found or the provider is invalid.
        """

        if provider == "static":
            if not key:
                log.error(
                    "[red]API.config[/red] - Key must be provided when using the `static` provider."
                )
                return None
            if key not in self._data or not self._data[key]:
                log.error(
                    f"[red]API.config[/red] - The key, `{key}` was not found or has no value in the environment."
                )
                return None
            log.warning(
                f"[green]API.config[/green] - The key, `{key}` was successfully loaded from the environment."
            )
            return self._data[key]
        elif provider == "dynamic":
            if not self._data:
                log.error(
                    "[red]API.config[/red] - No environment variables were loaded for the `dynamic` provider."
                )
                return None
            log.warning(
                "[green]API.config[/green] - Vital variables were successfully loaded into a temporary list for dynamic access."
            )
            return self._data
        else:
            log.error(
                "[red]API.config[/red] - Invalid provider. Please set the provider to either `dynamic` or `static`."
            )
            return None

class Configuration:
    def __init__(self):
        self.config = configparser.ConfigParser()

        home_dir = os.path.expanduser("~")
        config_dir = os.path.join(home_dir, ".sharded")
        os.makedirs(config_dir, exist_ok=True)

        config_path = os.path.join(config_dir, "sharded.ini")

        if not os.path.exists(config_path):
            console = Console()

            console.print(
                Panel(
                    "[yellow]Configuration file not found.[/yellow]\nAttempting to download latest configuration from GitHub...",
                    title="Config Status",
                    border_style="cyan",
                )
            )

            try:
                url = "https://raw.githubusercontent.com/ShardedInteractive/sharded/main/defaults/sharded.ini"
                response = requests.get(url, stream=True)
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))

                with Progress(
                    "[progress.description]{task.description}",
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    TimeRemainingColumn(),
                ) as progress:
                    task = progress.add_task(
                        "[cyan]Downloading config...", total=total_size
                    )

                    with open(config_path, "wb") as configfile:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                configfile.write(chunk)
                                progress.update(task, advance=len(chunk))

                console.print(
                    Panel(
                        "[green]Successfully downloaded default configuration from GitHub[/green]",
                        title="Download Complete",
                        border_style="green",
                    )
                )
            except Exception as e:
                console.print(
                    Panel(
                        f"[red]Failed to download configuration:[/red]\n{str(e)}",
                        title="Error",
                        border_style="red",
                    )
                )

        self.config.read(config_path)

    def get(self, section: str, key: str) -> str | None:
        value = self.config.get(section, key)
        return value
