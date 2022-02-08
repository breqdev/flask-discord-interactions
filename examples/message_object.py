import os
import sys

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import (DiscordInteractions,  # noqa: E402
                                        Message, Embed, embed)


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

discord.update_commands()


@discord.command()
def just_content(ctx):
    "Just normal string content"
    return "Just return a string to send it as a message"


@discord.command()
def markdown(ctx):
    "Fancy markdown tricks"
    return "All *the* **typical** ~~discord~~ _markdown_ `works` ***too.***"


@discord.command(name="embed")
def embed_(ctx):
    "Embeds!"

    return Message(embed=Embed(
        title="Embeds!",
        description="Embeds can be specified as Embed objects.",
        fields=[
            embed.Field(
                name="Can they use markdown?",
                value="**Yes!** [link](https://google.com/)"
            ),
            embed.Field(
                name="Where do I learn about how to format this object?",
                value=("[Try this visualizer!]"
                       "(https://leovoel.github.io/embed-visualizer/)")
            )
        ]
    ))


@discord.command()
def dict_embed(ctx):
    "Embeds as dict objects!"

    return Message(embed={
        "title": "Embeds!",
        "description": "Embeds can also be specified as JSON objects.",
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

    return Message(
        "Ephemeral messages are only sent to the user who ran the command, "
        "and they go away after a short while.\n\n"
        "Note that they cannot include files, "
        "but Markdown is *perfectly fine.*",
        ephemeral=True
    )


@discord.command()
def ephemeral_embed(ctx):
    "Ephemeral Message with an Embed"

    return Message(
        embed=Embed(
            title="Embeds!",
            description="Messages with Embeds can also be Ephemeral.",
            fields=[
                embed.Field(
                    name="Can they use markdown?",
                    value="**Yes!** [link](https://google.com/)"
                ),
                embed.Field(
                    name="Where do I learn about how to format this object?",
                    value=("[Try this visualizer!]"
                           "(https://leovoel.github.io/embed-visualizer/)")
                )
            ]
        ),
        ephemeral=True
    )


discord.set_route("/interactions")
discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
