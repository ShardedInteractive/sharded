---
title: What are Addons?
description: Learn about Sharded Addons and how to get started developing them.
---

Sharded Addons are **3rd party extensions** that integrate with Sharded Services and API while adding more commands, 
extended logic, and customization options. 

!!! question "What are the difference between Addons and Cogs?"
    Addons are **not officially** supported by **Sharded Interactive** thus allowing for 3rd party developers to create their own
    addons without worrying about our security and code guidelines.

    Cogs[^1] are **officially** supported by **Sharded Interactive** which follows out security and code guidelines and don't have to worry
    about potential security flaws or concerns with 3rd party addons.
    
    [^1]: More documentation related to discord.py cogs can be found [here.](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html) While we can use the same system, for ease-of-use and stability, we chose to develop an addon system on top of discord.py's cogs systems.

??? warning "Potential security risks or performance issues with Sharded Addons"
    Individual addons developed by **3rd party developers** can potentially contain security risks or performance issues about Sharded systems. 
    If you're worried about those risks then look for **'Sharded Approved'** when downloading addons.
