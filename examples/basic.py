import os

from flask import Flask
from flask_discord_interactions import (DiscordInteractions,
                                        InteractionResponse,
                                        CommandOptionType)


app = Flask(__name__)
discord = DiscordInteractions(app)


app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


@discord.command()
def ping(ctx):
    "Respond with a friendly 'pong'!"
    return "Pong!"


@discord.command(name="avatar", description="Show your user info")
def _avatar(ctx):
    return InteractionResponse(embed={
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
            }
        ],
        "image": {"url": ctx.author.avatar_url}
    })


@discord.command(options=[{
    "name": "message",
    "description": "The message to repeat",
    "type": CommandOptionType.STRING,
    "required": True
}])
def repeat(ctx, message):
    "Repeat the message (and escape mentions)"
    return InteractionResponse(
        f"{ctx.author.display_name} says {message}!",
        allowed_mentions={"parse": []},
        with_source=False
    )


@discord.command()
def noop(ctx):
    "Do nothing."
    print(ctx.token)
    return None


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
    return InteractionResponse(f"{ctx.author.display_name} chooses {choice}!")


discord.set_route("/interactions")


@app.route("/")
def index():
    return "Normal Flask routes work too!"


discord.clear_slash_commands(guild_id=os.environ["TESTING_GUILD"])
discord.register_slash_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
