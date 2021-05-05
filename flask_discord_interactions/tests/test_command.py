import pytest


def test_invalid_name(discord):
    with pytest.raises(ValueError):
        @discord.command()
        def sh(ctx):
            return "this shouldn't work..."


def test_provided_name(discord, client):
    @discord.command(name="other")
    def fn(ctx):
        return "hi"

    assert client.run("other").content == "hi"
