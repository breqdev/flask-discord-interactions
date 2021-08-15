from flask import Flask

from flask_discord_interactions import DiscordInteractions, ResponseType, InteractionType

def test_register_command():
    app = Flask(__name__)
    app.config["DONT_VALIDATE_SIGNATURE"] = True
    app.config["DONT_REGISTER_WITH_DISCORD"] = True

    discord = DiscordInteractions(app)

    @discord.command()
    def ping(ctx):
        return "pong"

    discord.update_slash_commands()


def test_register_subcommand():
    app = Flask(__name__)
    app.config["DONT_VALIDATE_SIGNATURE"] = True
    app.config["DONT_REGISTER_WITH_DISCORD"] = True

    discord = DiscordInteractions(app)

    group = discord.command_group("group")

    @group.command()
    def subcommand(ctx):
        return "pong"

    discord.update_slash_commands()


def test_register_options():
    app = Flask(__name__)
    app.config["DONT_VALIDATE_SIGNATURE"] = True
    app.config["DONT_REGISTER_WITH_DISCORD"] = True

    discord = DiscordInteractions(app)

    @discord.command()
    def ping(ctx, option1: str, option2: float, option3: str = ""):
        return f"pong"

    discord.update_slash_commands()


def test_register_subcommand_options():
    app = Flask(__name__)
    app.config["DONT_VALIDATE_SIGNATURE"] = True
    app.config["DONT_REGISTER_WITH_DISCORD"] = True

    discord = DiscordInteractions(app)

    group = discord.command_group("group")

    @group.command()
    def subcommand(ctx, option1: str, option2: float, option3: str = ""):
        return "pong"

    discord.update_slash_commands()
