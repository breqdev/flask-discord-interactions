import os
import sys

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import DiscordInteractions, Permission, Member


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]
app.config[
    "DISCORD_SCOPE"
] = "applications.commands.update applications.commands.permissions.update"

discord.update_commands()


@discord.command(default_member_permissions=4)
def blacklist(ctx, user: Member):
    "Only members with the 'Ban members' permission can use this command"
    return f"{user.username} has been blacklisted!"


@discord.command(
    default_member_permissions=8,
)
def command_with_perms(ctx):
    "You need a certain role to access this command"

    return "You have permissions!"


@discord.command(default_member_permissions=8)
def locked_command(ctx):
    "Secret command that has to be unlocked"

    return "You have unlocked the secret command!"


@discord.command()
def unlock_command(ctx):
    "Unlock the secret command"

    DiscordInteractions.set_permission_overwrites(
        permissions=[Permission(user=ctx.author.id)],
        command_id=locked_command.id,
        guild_id=ctx.guild_id,
        app=app,
    )

    return "Unlocked!"


discord.set_route("/interactions")

discord.update_commands(guild_id=os.environ["TESTING_GUILD"])

discord.set_permission_overwrites(
    [Permission(role="786840072891662336")],
    command_with_perms,
    guild_id=int(os.environ["TESTING_GUILD"]),
)


if __name__ == "__main__":
    app.run()
