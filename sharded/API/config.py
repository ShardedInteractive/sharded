import logging
import discord
import os
import configparser
import requests
from dotenv import load_dotenv
from rich.progress import Progress, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.console import Console

log = logging.getLogger("discord")

class Environment:
    "`Environment` is a class that provides a way to dynamically or static load environment variables from a `.env` file."
    load_dotenv()
    
    @staticmethod
    def vital(key: str = None, provider: str = None) -> str:
        """vital is a method that provides a way to dynamically or static load important environment variables from a `.env` file.

        Args:
            key (str): The value in which you want to receive from the environment. (Can be optional if `dynamic` is the provider.)
            provider (str): `static` will only get you the requested environmental variable. `dynamic` will give you access to a database for easier access to environmental variables. Defaults to `static`.

        Returns:
            str: The value of the environmental variable requested.
            dict: If `provider` is set to `dynamic`, a dictionary will be returned with all the environmental variables loaded into a temporary database.
        """

        database = {
            "DISCORD_TOKEN": os.getenv('DISCORD_TOKEN'),
            "DISCORD_PREFIX": os.getenv('DISCORD_PREFIX'),
            "GUILD_ID": discord.Object(id=os.getenv('GUILD_ID'))
        }

        if provider == "static":
            if key not in database:
                log.error(f"[red]API.config[/red] - The key, `{key}` was not found in the environment.")
                return None
            log.warning(f"[green]API.config[/green] - The key, `{key}` was loaded from the environment.")
            return database[key]
        elif provider == "dynamic":
            log.warning("[green]API.config[/green] - Vital variables were loaded into a temporary OR permanent list for dynamic access to keys or unknown.")
            return database
        else:
            log.error("[red]API.config[/red] - Provider was not set to `dynamic` or `static`. Please set the provider to either of the two options.")
            return None

