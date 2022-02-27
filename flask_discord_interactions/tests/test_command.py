from flask_discord_interactions.tests.conftest import client
from flask_discord_interactions.context import ApplicationCommandType
import pytest


def test_invalid_name(discord):
    with pytest.raises(ValueError):

        @discord.command()
        def this_is_a_very_long_command_name_that_will_raise_an_error(ctx):
            return "this shouldn't work..."


def test_provided_name(discord, client):
    @discord.command(name="other")
    def fn(ctx):
        return "hi"

    assert client.run("other").content == "hi"


def test_uppercase_name(discord):
    with pytest.raises(ValueError):

        @discord.command()
        def UPPERCASE(ctx):
            return "this shouldn't work..."


def test_invalid_character(discord):
    with pytest.raises(ValueError):

        @discord.command(name="invalid&character")
        def invalid_character(ctx):
            return "this shouldn't work..."


def test_type_user_valid(discord, client):
    @discord.command(name="testuser", type=ApplicationCommandType.USER)
    def fn(ctx, user):
        return "hi user"

    assert client.run("testuser").content == "hi user"


def test_type_message_valid(discord, client):
    @discord.command(name="testmessage", type=ApplicationCommandType.MESSAGE)
    def fn(ctx, message):
        return "message"

    assert client.run("testmessage").content == "message"


def test_type_user_valid_uppercase(discord, client):
    @discord.command(name="TEST USER", type=ApplicationCommandType.USER)
    def fn(ctx, user):
        return "hi user"

    assert client.run("TEST USER").content == "hi user"


def test_type_message_valid_uppercase(discord, client):
    @discord.command(name="TEST MSG", type=ApplicationCommandType.MESSAGE)
    def fn(ctx, message):
        return "message"

    assert client.run("TEST MSG").content == "message"
