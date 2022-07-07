import os
import sys
import enum
import math
import threading

import requests
from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import (
    DiscordInteractions,
    Message,
    Attachment,
    Member,
    Channel,
    Role,
    Option,
)


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

discord.update_commands()


# To specify options, include them with type annotations, just like Discord.py
# The annotations dict is used to provide a description for each option
# (they default to "no description")
@discord.command(annotations={"message": "The message to repeat"})
def repeat(ctx, message: str = "Hello!"):
    "Repeat the message (and escape mentions)"
    return Message(
        f"{ctx.author.display_name} says {message}!",
        allowed_mentions={"parse": []},
    )


# You can use str, int, or bool
@discord.command()
def add_one(ctx, number: int):
    return Message(str(number + 1), ephemeral=True)


@discord.command()
def and_gate(ctx, a: bool, b: bool):
    return f"{a} AND {b} is {a and b}"


@discord.command()
def sin(ctx, x: float):
    return f"sin({x}) = {math.sin(x)}"


# For using the "choices" field, you can use an Enum
class Animal(enum.Enum):
    Dog = "dog"
    Cat = "cat"


@discord.command(annotations={"choice": "Your favorite animal"})
def favorite(ctx, choice: Animal):
    "What is your favorite animal?"
    return f"{ctx.author.display_name} chooses {choice}!"


# This is also handy if you want to use the same options across multiple
# commands
@discord.command(annotations={"choice": "The animal you hate the most"})
def hate(ctx, choice: Animal):
    "What is the animal you hate the most?"
    return f"{ctx.author.display_name} hates {choice}s."


# You can also use IntEnum to receive the value as an integer
class BigNumber(enum.IntEnum):
    thousand = 1_000
    million = 1_000_000
    billion = 1_000_000_000
    trillion = 1_000_000_000_000


@discord.command(annotations={"number": "A big number"})
def big_number(ctx, number: BigNumber):
    "Print out a large number"
    return f"One more than the number is {number+1}."


# For User, Channel, and Role options, your function is passed an object
# that provides information about the resource
# You can access data about users with the context object
@discord.command(annotations={"user": "The user to show information about"})
def avatar_of(ctx, user: Member):
    "Show someone else's user info"
    return Message(
        embed={
            "title": user.display_name,
            "description": "Avatar Info",
            "fields": [
                {
                    "name": "Username",
                    "value": (f"**{user.username}**" f"#{user.discriminator}"),
                },
                {"name": "User ID", "value": user.id},
            ],
            "image": {"url": user.avatar_url},
        }
    )


@discord.command()
def has_role(ctx, user: Member, role: Role):
    if role.id in user.roles:
        return f"Yes, user {user.display_name} has role {role.name}."
    else:
        return f"No, user {user.display_name} does not have role {role.name}."


@discord.command()
def channel_info(ctx, channel: Channel):
    return Message(
        embed={
            "title": channel.name,
            "fields": [{"name": "Channel ID", "value": channel.id}],
        }
    )


# The Attachment object has some information about the attachment, including the URL
@discord.command()
def image(ctx, attachment: Attachment):
    return Message(
        embed={
            "title": attachment.filename,
            "description": "Image Info",
            "fields": [
                {
                    "name": "File Size",
                    "value": f"{attachment.size / 1024} KB",
                },
                {"name": "URL", "value": attachment.url},
            ],
            "image": {"url": attachment.url},
        }
    )


# To handle the attachment body itself, use a library like `requests` to fetch the resource
@discord.command()
def textfile(ctx, attachment: Attachment):
    response = requests.get(attachment.url)
    response.raise_for_status()

    return response.text


# For large files, this might take a while, so you may want to use a background thread
# if the file could be slow to download or if you perform heavy processing
# (remember, Discord enforces that you give an initial response within 3 seconds)
@discord.command()
def hexdump(ctx, attachment: Attachment):
    def do_read():
        response = requests.get(attachment.url)
        response.raise_for_status()

        dump = "```\n"
        for line in response.iter_content(chunk_size=16):
            dump += " ".join(f"{x:02x}" for x in line) + "\n"

            if len(dump) > 1900:
                dump += "...\n"
                break

        dump += "```"
        ctx.edit(dump)

    thread = threading.Thread(target=do_read)
    thread.start()

    return Message(deferred=True)


# You can also pass in a list of Option objects
@discord.command(
    options=[
        Option(
            name="message", type=str, description="The message to repeat", required=True
        ),
        Option(
            name="times",
            type=int,
            description="How many times to repeat the message",
            required=True,
        ),
    ]
)
def repeat_many(ctx, message: str, times: int):
    return " ".join([message] * times)


discord.set_route("/interactions")
discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == "__main__":
    app.run()
