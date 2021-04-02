import sys
import os
import threading
import time

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import (DiscordInteractions,  # noqa: E402
                                        DiscordInteractionsBlueprint,
                                        InteractionResponse,
                                        CommandOptionType,
                                        Member, Role, Channel)


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
# You have to define the embed JSON manually (see API docs)
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


# To specify options, include them with type annotations, just like Discord.py
@discord.command(annotations={"message": "The message to repeat"})
def repeat(ctx, message: str = "Hello!"):
    "Repeat the message (and escape mentions)"
    return InteractionResponse(
        f"{ctx.author.display_name} says {message}!",
        allowed_mentions={"parse": []},
    )


# You can access data about users with the context object
@discord.command(annotations={"user": "The user to show information about"})
def avatar_of(ctx, user: Member):
    "Show someone else's user info"
    return InteractionResponse(embed={
        "title": user.display_name,
        "description": "Avatar Info",
        "fields": [
            {
                "name": "Username",
                "value": (f"**{user.username}**"
                          f"#{user.discriminator}")
            },
            {
                "name": "User ID",
                "value": user.id
            }
        ],
        "image": {"url": user.avatar_url}
    })


# Role info is also available
@discord.command()
def has_role(ctx, user: Member, role: Role):
    if role.id in user.roles:
        return f"Yes, user {user.display_name} has role {role.name}."
    else:
        return f"No, user {user.display_name} does not have role {role.name}."


# Channel info, too!
@discord.command()
def channel_info(ctx, channel: Channel):
    return InteractionResponse(embed={
        "title": channel.name,
        "description": channel.topic,
        "fields": [
            {
                "name": "Channel ID",
                "value": channel.id
            },
            {
                "name": "NSFW?",
                "value": "Yes" if channel.nsfw else "No"
            }
        ]
    })


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


# You can use a decorator syntax to define subcommands
comic = discord.command_group("comic")


@comic.command()
def xkcd(ctx, number: int):
    return f"https://xkcd.com/{number}/"


@comic.command()
def homestuck(ctx, number: int):
    return f"https://homestuck.com/story/{number}"


# Subcommand groups are also supported
# Use ephemeral=True to only display the response to the user
base = discord.command_group("base", "Convert a number between bases")

base_to = base.subgroup("to", "Convert a number into a certain base")
base_from = base.subgroup("from", "Convert a number out of a certian base")


@base_to.command(name="bin")
def base_to_bin(ctx, number: int):
    "Convert a number into binary"
    return InteractionResponse(bin(number), ephemeral=True)


@base_to.command(name="hex")
def base_to_hex(ctx, number: int):
    "Convert a number into hexadecimal"
    return InteractionResponse(hex(number), ephemeral=True)


@base_from.command(name="bin")
def base_from_bin(ctx, number: str):
    "Convert a number out of binary"
    return InteractionResponse(int(number, base=2), ephemeral=True)


@base_from.command(name="hex")
def base_from_hex(ctx, number: str):
    "Convert a number out of hexadecimal"
    return InteractionResponse(int(number, base=16), ephemeral=True)


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


# You can set deferred=True to display a loading state to the user
@discord.command()
def delay(ctx, duration: int):
    def do_delay():
        time.sleep(duration)

        ctx.edit("Hiya!")

    thread = threading.Thread(target=do_delay)
    thread.start()

    return InteractionResponse(deferred=True)


# Here's an invalid command just to test things out
# @discord.command(name="s", description="name too short")
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
# This also removes old/unused slash commands
discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
