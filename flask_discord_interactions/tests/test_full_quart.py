import pytest
import asyncio
import sys

from quart import Quart


@pytest.fixture
def mock_flask():
    del sys.modules["flask"]
    import quart.flask_patch
    yield None
    del sys.modules["flask"]


@pytest.mark.asyncio
async def test_full_server(mock_flask):
    del sys.modules["flask_discord_interactions"]
    del sys.modules["flask_discord_interactions.discord"]

    from flask_discord_interactions import (DiscordInteractions,
                                        InteractionType, ResponseType)

    app = Quart("test_quart")
    app.config["DONT_VALIDATE_SIGNATURE"] = True
    app.config["DONT_REGISTER_WITH_DISCORD"] = True

    discord = DiscordInteractions(app)

    @discord.command()
    async def wait(ctx):
        await asyncio.sleep(0.01)
        return "Hi!"

    discord.set_route_async("/interactions")

    client = app.test_client()

    response = await client.post("/interactions", json={
        "type": InteractionType.APPLICATION_COMMAND,
        "id": 1,
        "channel_id": "",
        "guild_id": "",
        "token": "",
        "data": {
            "id": 1,
            "name": "wait"
        }
    })

    assert response.status_code == 200

    json = await response.get_json()

    assert json["type"] == \
        ResponseType.CHANNEL_MESSAGE_WITH_SOURCE

    assert json["data"]["content"] == "Hi!"
