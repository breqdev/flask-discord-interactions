import os
import sys

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import (DiscordInteractions,  # noqa: E402
                                        Response)


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

discord.update_commands()


# The "ctx" parameter is an Context object
# it works similarly to Context in Discord.py
@discord.command()
def avatar(ctx):
    "Show your user info"

    # You have to define the embed JSON manually for now (see API docs)
    return Response(embed={
        "title": ctx.author.display_name,
        "description": "Avatar Info",
        "fields": [
            {
                "name": "Member Since",
                "value": ctx.author.joined_at
            },
            {
                "name": "Username",
                "value": (f"**{ctx.author.username}**"
                          f"#{ctx.author.discriminator}")
            },
            {
                "name": "User ID",
                "value": ctx.author.id
            },
            {
                "name": "Channel ID",
                "value": ctx.channel_id
            },
            {
                "name": "Guild ID",
                "value": ctx.guild_id
            }
        ],
        "image": {"url": ctx.author.avatar_url}
    })


# You can use this to implement a rudimentary server-side permissions system
@discord.command()
def admin_only(ctx):
    if not ctx.author.permissions & 8:
        return Response(
            content="Only administrators are allowed to use this command",
            ephemeral=True
        )

    return "Hello!"


@discord.command()
def restricted(ctx, special_option: str = None):
    "Only manage_messages can set special_option"

    if not ctx.author.permissions & 16:  # MANAGE_MESSAGES
        if special_option is not None:
            return "Need permissions to use special_option"

    if special_option is not None:
        return "You have used the special option!"
    else:
        return "You have not used the special option."


discord.set_route("/interactions")
discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
