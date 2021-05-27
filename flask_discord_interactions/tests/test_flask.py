from flask import Flask

from flask_discord_interactions import DiscordInteractions, ResponseType


def test_flask():
    app = Flask(__name__)
    app.config["DONT_VALIDATE_SIGNATURE"] = True
    app.config["DONT_REGISTER_WITH_DISCORD"] = True

    discord = DiscordInteractions(app)

    @discord.command()
    def ping(ctx, pong: str = "ping"):
        return f"Ping {pong}!"

    discord.set_route("/interactions")

    with app.test_client() as client:
        response = client.post("/interactions", json={
            "id": 1,
            "channel_id": "",
            "guild_id": "",
            "token": "",
            "data": {
                "id": 1,
                "name": "ping",
                "options": [
                    {
                        "type": 1,
                        "name": "Pong"
                    }
                ]
            },
            "member": {
                "id": 1,
                "nick": "",
                "user": {
                    "id": 1,
                    "username": "test"
                }
            }
        })

        assert response.status_code == 200
        assert response.get_json()["type"] == \
            ResponseType.CHANNEL_MESSAGE_WITH_SOURCE

        assert response.get_json()["data"]["content"] == "Ping Pong!"

def test_app_factory():
    discord = DiscordInteractions()

    @discord.command()
    def ping(ctx, pong: str = "ping"):
        return f"Ping {pong}!"

    def create_app():
        app = Flask(__name__)
        discord.init_app(app)
        discord.set_route("/interactions", app=app)
        return app

    app = create_app()
    app.config["DONT_VALIDATE_SIGNATURE"] = True
    app.config["DONT_REGISTER_WITH_DISCORD"] = True

    with app.test_client() as client:
        response = client.post("/interactions", json={
            "id": 1,
            "channel_id": "",
            "guild_id": "",
            "token": "",
            "data": {
                "id": 1,
                "name": "ping",
                "options": [
                    {
                        "type": 1,
                        "name": "Pong"
                    }
                ]
            },
            "member": {
                "id": 1,
                "nick": "",
                "user": {
                    "id": 1,
                    "username": "test"
                }
            }
        })

        assert response.status_code == 200
        assert response.get_json()["type"] == \
            ResponseType.CHANNEL_MESSAGE_WITH_SOURCE

        assert response.get_json()["data"]["content"] == "Ping Pong!"



