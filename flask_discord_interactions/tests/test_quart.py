import asyncio

import pytest
from quart import Quart

from flask_discord_interactions import (
    DiscordInteractions,
    Client,
    Message,
    AsyncContext,
)


@pytest.fixture()
def quart_discord():
    app = Quart(__name__)
    app.config["DONT_VALIDATE_SIGNATURE"] = True
    app.config["DONT_REGISTER_WITH_DISCORD"] = True

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


@pytest.mark.asyncio
async def test_mixed_commands(quart_discord):
    discord, client = quart_discord

    @discord.command()
    async def async_command(ctx):
        return "Async"

    @discord.command()
    def not_async_command(ctx):
        return "Not Async"

    assert (await client.run("async_command")).content == "Async"
    assert client.run("not_async_command").content == "Not Async"


@pytest.mark.asyncio
async def test_followup(quart_discord):
    discord, client = quart_discord

    followup_task = None

    @discord.command()
    async def followup(ctx):
        nonlocal followup_task

        async def do_followup():
            await ctx.edit(f"Hello!")

        followup_task = asyncio.create_task(do_followup())
        return Message(deferred=True)

    with client.context(AsyncContext()):
        await client.run("followup")
    await followup_task
