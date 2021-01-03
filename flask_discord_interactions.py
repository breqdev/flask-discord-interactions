import time

import requests

from flask import current_app, request, jsonify

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey


class InteractionType:
    PING = 1
    APPLICATION_COMMAND = 2


class InteractionResponseType:
    PONG = 1
    ACKNOWLEDGE = 2
    CHANNEL_MESSAGE = 3
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    ACKNOWLEDGE_WITH_SOURCE = 5


class CommandOptionType:
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


class InteractionContext:
    class InteractionAuthor:
        def __init__(self, data=None):
            if data:
                self.id = data["user"]["id"]
                self.username = data["user"]["username"]
                self.nick = data["nick"]

        @property
        def display_name(self):
            return self.nick or self.username

    def __init__(self, data=None):
        if data:
            self.author = self.InteractionAuthor(data["member"])
            self.id = data["id"]
            self.channel_id = data["channel_id"]
            self.guild_id = data["guild_id"]


class InteractionResponse:
    def __init__(self, content=None, *, tts=False, embed=None, embeds=None,
                 allowed_mentions={"parse": ["roles", "users", "everyone"]},
                 with_source=True):
        self.content = content
        self.tts = tts

        if embed is not None and embeds is not None:
            raise ValueError("Specify only one of embed or embeds")
        if embed is not None:
            embeds = [embed]

        self.embeds = embeds
        self.allowed_mentions = allowed_mentions

        if self.embeds is not None or self.content is not None:
            if with_source:
                self.response_type = \
                    InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE
            else:
                self.response_type = InteractionResponseType.CHANNEL_MESSAGE
        else:
            if with_source:
                self.response_type = \
                    InteractionResponseType.ACKNOWLEDGE_WITH_SOURCE
            else:
                self.response_type = InteractionResponseType.ACKNOWLEDGE

    def dump(self):
        return {
            "type": self.response_type,
            "data": {
                "content": self.content,
                "tts": self.tts,
                "embeds": self.embeds,
                "allowed_mentions": self.allowed_mentions
            }
        }


class SlashCommand:
    def __init__(self, command, name, description, options):
        self.command = command
        self.name = name
        self.description = description
        self.options = options

    def create_kwargs(self, data):
        if "options" not in data["data"]:
            return {}

        kwargs = {}
        for option in data["data"]["options"]:
            kwargs[option["name"]] = option["value"]
        return kwargs

    def run(self, data):
        context = InteractionContext(data)
        return self.command(context, **self.create_kwargs(data))


class DiscordInteractions:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault("DISCORD_CLIENT_ID", "")
        app.config.setdefault("DISCORD_PUBLIC_KEY", "")
        app.config.setdefault("DISCORD_CLIENT_SECRET", "")
        app.discord_commands = {}

    def fetch_token(self, app=None):
        if app is None:
            app = self.app

        response = requests.post(
            "https://discord.com/api/v8/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "scope": "applications.commands.update"
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            auth=(
                app.config["DISCORD_CLIENT_ID"],
                app.config["DISCORD_CLIENT_SECRET"]
            )
        )

        response.raise_for_status()
        app.discord_token = response.json()  # TODO: handle token expiration
        app.discord_token["expires_on"] = (time.time()
                                           + app.discord_token["expires_in"]/2)

    def auth_headers(self, app):
        if time.time() > app.discord_token["expires_on"]:
            print("Refreshing token")
            self.fetch_token(app)
        return {"Authorization": f"Bearer {app.discord_token['access_token']}"}

    def clear_slash_commands(self, app=None, guild_id=None):
        if app is None:
            app = self.app

        if guild_id:
            url = ("https://discord.com/api/v8/applications/"
                   f"{app.config['DISCORD_CLIENT_ID']}/"
                   f"guilds/{guild_id}/commands")
        else:
            url = ("https://discord.com/api/v8/applications/"
                   f"{app.config['DISCORD_CLIENT_ID']}/commands")

        response = requests.get(url, headers=self.auth_headers(app))
        response.raise_for_status()

        for command in response.json():
            id = command["id"]

            if guild_id:
                url = ("https://discord.com/api/v8/applications/"
                       f"{app.config['DISCORD_CLIENT_ID']}/"
                       f"guilds/{guild_id}/commands/{id}")
            else:
                url = ("https://discord.com/api/v8/applications/"
                       f"{app.config['DISCORD_CLIENT_ID']}/commands/{id}")

            response = requests.delete(url, headers=self.auth_headers(app))
            response.raise_for_status()

    def register_slash_commands(self, app=None, guild_id=None):
        if app is None:
            app = self.app

        for command in app.discord_commands.values():
            if guild_id:
                url = ("https://discord.com/api/v8/applications/"
                       f"{app.config['DISCORD_CLIENT_ID']}/"
                       f"guilds/{guild_id}/commands")
            else:
                url = ("https://discord.com/api/v8/applications/"
                       f"{app.config['DISCORD_CLIENT_ID']}/commands")

            json = {
                "name": command.name,
                "description": command.description,
                "options": command.options
            }

            response = requests.post(
                url, json=json, headers=self.auth_headers(app))
            response.raise_for_status()
            command.id = response.json()["id"]

    def add_slash_command(self, command, app=None, name=None,
                          description=None, options=[]):
        slash_command = SlashCommand(command, name, description, options)
        app.discord_commands[name] = slash_command

    def command(self, app=None, name=None, description=None, options=[]):
        "Decorator to create a Slash Command"
        if app is None:
            app = self.app

        def decorator(func):
            nonlocal app, name, description, options
            if name is None:
                name = func.__name__
            if description is None:
                description = func.__doc__
            self.add_slash_command(func, app, name, description, options)
            return func

        return decorator

    def verify_signature(self, data, signature, timestamp):
        message = timestamp.encode() + data
        verify_key = VerifyKey(
            bytes.fromhex(current_app.config["DISCORD_PUBLIC_KEY"]))
        try:
            verify_key.verify(message, bytes.fromhex(signature))
        except BadSignatureError:
            return False
        else:
            return True

    def run_command(self, data):
        command_name = data["data"]["name"]

        slash_command = current_app.discord_commands.get(command_name)

        if slash_command is None:
            raise ValueError(f"Invalid command name: {slash_command}")

        return slash_command.run(data)

    def set_route(self, route, app=None):
        if app is None:
            app = self.app

        @app.route(route, methods=["POST"])
        def interactions():
            signature = request.headers.get('X-Signature-Ed25519')
            timestamp = request.headers.get('X-Signature-Timestamp')

            if (signature is None or timestamp is None
                    or not self.verify_signature(
                    request.data, signature, timestamp)):
                return "Bad Request Signature", 401

            if (request.json
                    and request.json.get("type") == InteractionType.PING):
                return jsonify({
                    "type": InteractionResponseType.PONG
                })

            result = self.run_command(request.json)

            response = {}

            if result is None:
                response = InteractionResponse()
            elif isinstance(result, str):
                response = InteractionResponse(result)
            elif isinstance(result, InteractionResponse):
                response = result
            else:
                raise ValueError("Command returned invalid response")

            return jsonify(response.dump())
