import asyncio

import pytest

@pytest.fixture()
def quart_discord():
    import sys
    del sys.modules["flask"]

    from quart import Quart
    import quart.flask_patch


    from flask_discord_interactions import DiscordInteractions, Client


    app = Quart(__name__)
    discord = DiscordInteractions(app)
    return discord, Client(discord)


@pytest.mark.asyncio
async def test_async_ping(quart_discord):
    discord, client = quart_discord

    @discord.command()
    async def ping(ctx, pong: str = "pong"):
        "Respond with a friendly 'pong'!"
        return f"Pong {pong}!"

    assert (await client.run("ping")).content == "Pong pong!"


@pytest.mark.asyncio
async def test_await_in_command(quart_discord):
    discord, client = quart_discord

    @discord.command()
    async def wait(ctx):
        await asyncio.sleep(0.01)
        return "Hi!"

    assert (await client.run("wait")).content == "Hi!"