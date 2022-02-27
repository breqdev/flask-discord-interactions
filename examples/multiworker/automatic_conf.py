import os
import sys

sys.path.insert(1, "examples/multiworker")

from automatic import discord


def on_starting(server):
    print("registering commands!")
    discord.update_commands(guild_id=os.environ["TESTING_GUILD"])
