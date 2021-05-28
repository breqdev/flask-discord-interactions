from flask_discord_interactions import (Response, ResponseType, ActionRow,
                                        Button, ComponentType, ButtonStyles)


def test_action_row(discord, client):
    @discord.command()
    def action_row(ctx):
        return Response(
            content="Hi!",
            components=[
                ActionRow()
            ]
        )

    expected = {
        "type": ResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {
            "content": "Hi!",
            "embeds": None,
            "flags": 0,
            "tts": False,
            "allowed_mentions": {"parse": ["roles", "users", "everyone"]},
            "components": [{
                "type": ComponentType.ACTION_ROW
            }]
        }
    }

    assert client.run("action_row").dump() == expected


def test_button(discord, client):
    @discord.command()
    def button(ctx):
        return Response(
            content="Hi!",
            components=[
                ActionRow(components=[
                    Button(
                        style=ButtonStyles.PRIMARY,
                        custom_id="my_button",
                        label="My Button"
                    )
                ])
            ]
        )

    expected = {
        "type": ResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {
            "content": "Hi!",
            "embeds": None,
            "flags": 0,
            "tts": False,
            "allowed_mentions": {"parse": ["roles", "users", "everyone"]},
            "components": [{
                "type": ComponentType.ACTION_ROW,
                "components": [{
                    "type": ComponentType.BUTTON,
                    "style": ButtonStyles.PRIMARY,
                    "custom_id": "my_button",
                    "label": "My Button",
                    "disabled": False
                }]
            }]
        }
    }

    assert client.run("button").dump() == expected
