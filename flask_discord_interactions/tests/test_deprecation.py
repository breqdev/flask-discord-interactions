import pytest

from flask import Flask
from flask_discord_interactions import DiscordInteractions, SlashCommand, Response


def test_slash_command(discord, client):
    with pytest.deprecated_call():
        command = SlashCommand(lambda ctx: "ping", "ping", "No description", [], [])

    # make sure the object still works
    assert command.name == "ping"


def test_response():
    with pytest.deprecated_call():
        response = Response("Hello this is my response")

    assert response.content == "Hello this is my response"


def test_add_slash_command(discord):
    with pytest.deprecated_call():
        discord.add_slash_command(lambda ctx: "ping", "ping", "test test test", [], [])

    assert discord.discord_commands["ping"].description == "test test test"


def test_update_slash_commands():
    app = Flask(__name__)
    app.config["DONT_VALIDATE_SIGNATURE"] = True
    app.config["DONT_REGISTER_WITH_DISCORD"] = True

    discord = DiscordInteractions(app)

    with pytest.deprecated_call():
        discord.update_slash_commands()
