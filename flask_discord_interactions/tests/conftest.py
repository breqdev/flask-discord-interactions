import pytest

from flask import Flask

from flask_discord_interactions import DiscordInteractions, Client


@pytest.fixture(scope="module")
def discord():
    app = Flask(__name__)
    return DiscordInteractions(app)


@pytest.fixture(scope="module")
def client(discord):
    return Client(discord)
