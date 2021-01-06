import os
import threading
import time

from flask import Flask
from flask_discord_interactions import (DiscordInteractions,
                                        DiscordInteractionsBlueprint,
                                        InteractionResponse,
                                        CommandOptionType)


app = Flask(__name__)
discord = DiscordInteractions(app)


# Find these in your Discord Developer Portal, store them as environment vars
app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


# Simplest type of command: respond with a string
@discord.command()
def ping(ctx):
    "Respond with a friendly 'pong'!"
    return "Pong!"


# You can specify a name and desc explicitly
# (otherwise it's inferred from function name and docstring)
# For more complex responses, return an InteractionResponse object
# You have to define the embed JSON manually
# Refer to Discord API documentation for details
# The "ctx" parameter is an InteractionContext object
# it works similarly to Context in Discord.py
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


# To specify options, include them as a list of JSON objects
# Refer to the Discord API documentation for details
# The CommandOptionType enum is helpful
# Options are passed as keyword arguments to the function
# Use "with_source=False" to supress the original command message
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


# Return None to not send a response
@discord.command()
def noop(ctx):
    "Do nothing."
    print(ctx.token)
    return None


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
    return InteractionResponse(f"{ctx.author.display_name} chooses {choice}!")


# Create Blueprint objects to split functionality across modules
bp = DiscordInteractionsBlueprint()


# Use them just like the DiscordInteractions object
@bp.command()
def blue(ctx):
    return ":blue_circle:"


# Register them to the DiscordInteractions object
discord.register_blueprint(bp)


# You can continue to send followup messages from background processes
# You can also send files now (although you can't with the initial response)
@discord.command()
def followup(ctx):
    def do_followup():
        print("Followup task started")
        time.sleep(5)
        print("Editing original message")
        ctx.edit("Editing my original message")
        time.sleep(5)
        print("Sending a file")
        ctx.send(InteractionResponse(
            content="Sending a file",
            file=("README.md", open("README.md", "r"), "text/markdown")))
        time.sleep(5)
        print("Deleting original message")
        ctx.delete()
        time.sleep(5)
        print("Sending new message")
        new_message = ctx.send("Sending a new message")
        time.sleep(5)
        print("Editing new message")
        ctx.edit("Editing a new message", message=new_message)

    thread = threading.Thread(target=do_followup)
    thread.start()

    return "Sending an original message"


# Here's a workaround you can do to send a file immediately
@discord.command()
def sendfile(ctx):
    def do_send():
        ctx.send(InteractionResponse(
            content="Here's my file!",
            file=("README.md", open("README.md", "r"), "text/markdown")
        ))

    thread = threading.Thread(target=do_send)
    thread.start()

    return None


# Here's an invalid command just to test things out
# @discord.command(name="s", description="name to short")
# def invalid(ctx):
#     return "This will never work..."


# This is the URL that your app will listen for Discord Interactions on
# Put this into the developer portal
discord.set_route("/interactions")


# Useful for hosting other content through your app
@app.route("/")
def index():
    return "Normal Flask routes work too!"


# Register slash commands with this
# (omit guild_id parameter to register global commands,
# but note that these can take up to 1 hour to be registered)
discord.register_slash_commands(guild_id=os.environ["TESTING_GUILD"])
# Clear old slash commands with this (optional, useful mostly for dev)
discord.clear_slash_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
