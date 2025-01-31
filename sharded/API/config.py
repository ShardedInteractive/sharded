import logging
import discord
import os
from dotenv import load_dotenv

log = logging.getLogger("discord")

class Environment:
    "`Environment` is a class that provides a way to dynamically or static load environment variables from a `.env` file."
    load_dotenv()
    
    @staticmethod
    def load_key(key: str = None, provider: str = None) -> str:
        "Returns a environment variable with a provided key or in other words, the name of the variable."

        database = {
            "DISCORD_TOKEN": os.getenv('DISCORD_TOKEN'),
            "DISCORD_PREFIX": os.getenv('DISCORD_PREFIX'),
            "GUILD_ID": discord.Object(id=os.getenv('GUILD_ID'))
        }

        if provider == "static":
            return database[key]
        elif provider == "dynamic":
            log.warning("[green]API.config[/green] - Environment variable were loaded into a temporary OR permanent database for dynamic access to keys or unknown.")
            return database

