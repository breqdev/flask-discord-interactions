import time
import json

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
                self.discriminator = data["user"]["discriminator"]
                self.avatar_hash = data["user"]["avatar"]
                self.bot = data["user"].get("bot", False)
                self.system = data["user"].get("system", False)
                self.mfa_enabled = data["user"].get("mfa_enabled", False)
                self.locale = data["user"].get("locale")
                self.flags = data["user"].get("flags")
                self.premium_type = data["user"].get("premium_type")
                self.public_flags = data["user"].get("public_flags")

                self.nick = data["nick"]
                self.roles = data["roles"]
                self.joined_at = data["joined_at"]
                self.premium_since = data.get("premium_since")
                self.deaf = data["deaf"]
                self.mute = data["mute"]
                self.pending = data.get("pending")

        @property
        def display_name(self):
            return self.nick or self.username

        @property
        def avatar_url(self):
            return ("https://cdn.discordapp.com/avatars/"
                    f"{self.id}/{self.avatar_hash}.png")

    def __init__(self, discord, app, data=None):
        self.client_id = app.config["DISCORD_CLIENT_ID"]
        self.auth_headers = discord.auth_headers(app)

        if data:
            self.author = self.InteractionAuthor(data["member"])
            self.id = data["id"]
            self.token = data["token"]
            self.channel_id = data["channel_id"]
            self.guild_id = data["guild_id"]
            self.options = data["data"].get("options")
            self.command_name = data["data"]["name"]
            self.command_id = data["data"]["id"]

    def followup_url(self, message=None):
        url = ("https://discord.com/api/v8/webhooks/"
               f"{self.client_id}/{self.token}")
        if message is not None:
            url += f"/messages/{message}"

        return url

    def edit(self, response, message="@original"):
        response = InteractionResponse.from_return_value(response)

        response = requests.patch(
            self.followup_url(message),
            json=response.dump_followup(),
            headers=self.auth_headers
        )
        response.raise_for_status()

    def delete(self, message="@original"):
        response = requests.delete(
            self.followup_url(message),
            headers=self.auth_headers
        )
        response.raise_for_status()

    def send(self, response):
        response = InteractionResponse.from_return_value(response)

        response = requests.post(
            self.followup_url(),
            headers=self.auth_headers,
            **response.dump_multipart()
        )
        response.raise_for_status()
        return response.json()["id"]


class InteractionResponse:
    def __init__(self, content=None, *, tts=False, embed=None, embeds=None,
                 allowed_mentions={"parse": ["roles", "users", "everyone"]},
                 with_source=True, file=None, files=None):
        self.content = content
        self.tts = tts

        if embed is not None and embeds is not None:
            raise ValueError("Specify only one of embed or embeds")
        if embed is not None:
            embeds = [embed]
        self.embeds = embeds

        if file is not None and files is not None:
            raise ValueError("Specify only one of file or files")
        if file is not None:
            files = [file]
        self.files = files

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

    @staticmethod
    def from_return_value(result):
        if result is None:
            return InteractionResponse()
        elif isinstance(result, InteractionResponse):
            return result
        else:
            return InteractionResponse(str(result))

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

    def dump_followup(self):
        return {
            "content": self.content,
            "tts": self.tts,
            "embeds": self.embeds,
            "allowed_mentions": self.allowed_mentions
        }

    def dump_multipart(self):
        if self.files:
            payload_json = json.dumps(self.dump_followup())

            multipart = []
            for file in self.files:
                multipart.append(("file", file))

            return {"data": {"payload_json": payload_json}, "files": multipart}
        else:
            return {"json": self.dump_followup()}


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

    def run(self, discord, app, data):
        context = InteractionContext(discord, app, data)
        return self.command(context, **self.create_kwargs(data))


class DiscordInteractionsBlueprint:
    def __init__(self):
        self.discord_commands = {}

    def add_slash_command(self, command, name=None,
                          description=None, options=[]):
        slash_command = SlashCommand(command, name, description, options)
        self.discord_commands[name] = slash_command

    def command(self, name=None, description=None, options=[]):
        "Decorator to create a Slash Command"
        def decorator(func):
            nonlocal name, description, options
            if name is None:
                name = func.__name__
            if description is None:
                description = func.__doc__ or "No description"
            self.add_slash_command(func, name, description, options)
            return func

        return decorator


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
        app.discord_token = None

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
        if (app.discord_token is None
                or time.time() > app.discord_token["expires_on"]):
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
                description = func.__doc__ or "No description"
            self.add_slash_command(func, app, name, description, options)
            return func

        return decorator

    def register_blueprint(self, blueprint, app=None):
        if app is None:
            app = self.app

        app.discord_commands.update(blueprint.discord_commands)

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

        return slash_command.run(self, current_app, data)

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

            response = InteractionResponse.from_return_value(result)

            return jsonify(response.dump())
