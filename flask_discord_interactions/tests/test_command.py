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