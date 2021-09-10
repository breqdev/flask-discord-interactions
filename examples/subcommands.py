import os
import sys
import time
import threading

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import DiscordInteractions, Message


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

discord.update_commands()


# You can use a decorator syntax to define subcommands
comic = discord.command_group("comic")


@comic.command()
def xkcd(ctx, number: int):
    return f"https://xkcd.com/{number}/"


@comic.command()
def homestuck(ctx, number: int):
    return f"https://homestuck.com/story/{number}"



# Subcommand groups are also supported
base = discord.command_group("base", "Convert a number between bases")

base_to = base.subgroup("to", "Convert a number into a certain base")
base_from = base.subgroup("from", "Convert a number out of a certian base")


@base_to.command(name="bin")
def base_to_bin(ctx, number: int):
    "Convert a number into binary"
    return Message(bin(number), ephemeral=True)


@base_to.command(name="hex")
def base_to_hex(ctx, number: int):
    "Convert a number into hexadecimal"
    return Message(hex(number), ephemeral=True)


@base_from.command(name="bin")
def base_from_bin(ctx, number: str):
    "Convert a number out of binary"
    return Message(int(number, base=2), ephemeral=True)


@base_from.command(name="hex")
def base_from_hex(ctx, number: str):
    "Convert a number out of hexadecimal"
    return Message(int(number, base=16), ephemeral=True)


# Subcommands have the same access to context
whatismy = discord.command_group("whatismy")


@whatismy.command()
def name(ctx):
    return ctx.author.display_name


@whatismy.command()
def discriminator(ctx):
    return ctx.author.discriminator

# And so do subcommands in subcommand groups
top_level = discord.command_group("toplevel")
second_level = top_level.subgroup("secondlevel")

@second_level.command()
def thirdlevel(ctx):
    def do_delay():
        time.sleep(1)

        ctx.edit(f"Hello, {ctx.author.display_name}!")

    thread = threading.Thread(target=do_delay)
    thread.start()

    return Message(deferred=True)


# Subcommands can send followup messages too
delay = discord.command_group("delay")

@delay.command()
def seconds(ctx, seconds: int):
    def do_delay():
        time.sleep(seconds)

        ctx.edit("Hiya!")

    thread = threading.Thread(target=do_delay)
    thread.start()

    return Message(deferred=True)

@delay.command()
def minutes(ctx, minutes: str):
    def do_delay():
        time.sleep(float(minutes) * 60)

        ctx.edit("Hiya!")

    thread = threading.Thread(target=do_delay)
    thread.start()

    return Message(deferred=True)


discord.set_route("/interactions")
discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
