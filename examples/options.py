import os
import sys

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import (DiscordInteractions,  # noqa: E402
                                        Response, CommandOptionType)


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

discord.update_slash_commands()


# To specify options, include them with type annotations, just like Discord.py
@discord.command(annotations={"message": "The message to repeat"})
def repeat(ctx, message: str = "Hello!"):
    "Repeat the message (and escape mentions)"
    return Response(
        f"{ctx.author.display_name} says {message}!",
        allowed_mentions={"parse": []},
    )


# Define choices in the options JSON, see Discord API docs for details
@discord.command(options=[{
    "name": "choice",
    "description": "Your favorite animal",
    "type": CommandOptionType.STRING,
    "required": True,
    "choices": [
        {
            "name": "Dog",
            "value": "dog"
        },
        {
            "name": "Cat",
            "value": "cat"
        }
    ]
}])
def favorite(ctx, choice):
    "What is your favorite animal?"
    return Response(f"{ctx.author.display_name} chooses {choice}!")


discord.set_route("/interactions")
discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
