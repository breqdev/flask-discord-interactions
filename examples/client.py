import sys

from flask import Flask

# This is just here for the sake of examples testing
# to make sure that the imports work
# (you don't actually need it in your code)
sys.path.insert(1, ".")

from flask_discord_interactions import (
    DiscordInteractions,
    Client,
    Message,
    CommandOptionType,
    Context,
    Member,
)


app = Flask(__name__)
discord = DiscordInteractions(app)

test_client = Client(discord)


# Simplest type of command: respond with a string
@discord.command()
def ping(ctx, pong: str = "pong"):
    "Respond with a friendly 'pong'!"
    return f"Pong {pong}!"


print(test_client.run("ping"))
print(test_client.run("ping", pong="ping"))


groupy = discord.command_group("groupy")


@groupy.command()
def group(ctx, embed: bool):
    if embed:
        return Message(embed={"title": "Groupy group"})
    else:
        return "Groupy group"


print(test_client.run("groupy", "group", True))
print(test_client.run("groupy", "group", False))


@discord.command(
    options=[
        {"type": CommandOptionType.SUB_COMMAND, "name": "subcommand_1"},
        {"type": CommandOptionType.SUB_COMMAND, "name": "subcommand_2"},
    ]
)
def manual_style_group(ctx, sub):
    return f"subcommand is {sub}"


print(test_client.run("manual_style_group", "subcommand_1"))
print(test_client.run("manual_style_group", "subcommand_2"))


@discord.command()
def uses_context(ctx):
    return f"Your name is {ctx.author.display_name}"


context = Context(author=Member(username="Bob"))

with test_client.context(context):
    print(test_client.run("uses_context"))
