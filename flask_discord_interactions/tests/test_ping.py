import pytest

from flask import Flask

from flask_discord_interactions import (DiscordInteractions,
                                        Client)

@pytest.fixture
def discord():
    app = Flask(__name__)
    return DiscordInteractions(app)

@pytest.fixture
def client(discord):
    return Client(discord)


def test_ping(discord, client):
    @discord.command()
    def ping(ctx, pong: str = "pong"):
        "Respond with a friendly 'pong'!"
        return f"Pong {pong}!"

    assert client.run("ping").content == "Pong pong!"
    assert client.run("ping", pong="sprong").content == "Pong sprong!"

