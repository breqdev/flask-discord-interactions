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

discord.update_slash_commands()


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


discord.set_route("/interactions")
discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
