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


@discord.command()
def just_content(ctx):
    "Just normal string content"
    return "Just return a string to send it as a message"


@discord.command()
def markdown(ctx):
    "Fancy markdown tricks"
    return "All *the* **typical** ~~discord~~ _markdown_ `works` ***too.***"


@discord.command()
def embed(ctx):
    "Embeds!"

    return Response(embed={
        "title": "Embeds!",
        "description": "Embeds must be specified as JSON objects.",
        "fields": [
            {
                "name": "Can they use markdown?",
                "value": "**Yes!** [link](https://google.com/)"
            },
            {
                "name": "Where do I learn about how to format this object?",
                "value": ("[Try this visualizer!]"
                          "(https://leovoel.github.io/embed-visualizer/)")
            }
        ]
    })


@discord.command()
def ephemeral(ctx):
    "Ephemeral Message"

    return Response(
        "Ephemeral messages are only sent to the user who ran the command, "
        "and they go away after a short while.\n\n"
        "Note that they cannot include embeds or files, "
        "but Markdown is *perfectly fine.*",
        ephemeral=True
    )


discord.set_route("/interactions")
discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
