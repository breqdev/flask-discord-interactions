import os
import sys

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import DiscordInteractions, Permission


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

discord.update_commands()


@discord.command(default_permission=False, permissions=[
    Permission(role="786840072891662336")
])
def command_with_perms(ctx):
    "You need a certain role to access this command"

    return "You have permissions!"


@discord.command(default_permission=False)
def locked_command(ctx):
    "Secret command that has to be unlocked"

    return "You have unlocked the secret command!"


@discord.command()
def unlock_command(ctx):
    "Unlock the secret command"

    ctx.overwrite_permissions(
        [Permission(user=ctx.author.id)], "locked_command")

    return "Unlocked!"


# Command groups can have permissions at the top level

group = discord.command_group("group", default_permission=False, permissions=[
    Permission(role="786840072891662336")
])

@group.command()
def locked_subcommand(ctx):
    "Locked subcommand"

    return "You have unlocked the secret subcommand!"


discord.set_route("/interactions")


discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
