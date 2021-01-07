import time

import requests

from flask import current_app, request, jsonify

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from .command import SlashCommand
from .response import InteractionResponse, InteractionResponseType


class InteractionType:
    PING = 1
    APPLICATION_COMMAND = 2


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

    def update_slash_commands(self, app=None, guild_id=None):
        if app is None:
            app = self.app

        needed = app.discord_commands.copy()

        if guild_id:
            url = ("https://discord.com/api/v8/applications/"
                   f"{app.config['DISCORD_CLIENT_ID']}/"
                   f"guilds/{guild_id}/commands")
        else:
            url = ("https://discord.com/api/v8/applications/"
                   f"{app.config['DISCORD_CLIENT_ID']}/commands")

        response = requests.get(url, headers=self.auth_headers(app))
        response.raise_for_status()
        current = response.json()

        for command in current:
            if command["name"] in needed:
                target = needed[command["name"]]
                if command["description"] == target.description:
                    if (not command.get("options") and not target.options
                            or command.get("options") == target.options):
                        del needed[command["name"]]

                        target.id = command["id"]
                        continue

            id = command["id"]
            if guild_id:
                delete_url = ("https://discord.com/api/v8/applications/"
                              f"{app.config['DISCORD_CLIENT_ID']}/"
                              f"guilds/{guild_id}/commands/{id}")
            else:
                delete_url = (
                    "https://discord.com/api/v8/applications/"
                    f"{app.config['DISCORD_CLIENT_ID']}/commands/{id}")

            response = requests.delete(
                delete_url, headers=self.auth_headers(app))
            response.raise_for_status()

        for name, command in needed.items():
            json = {
                "name": command.name,
                "description": command.description,
                "options": command.options
            }

            response = requests.post(
                url, json=json, headers=self.auth_headers(app))
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                raise ValueError(
                    f"Unable to register command {command.name} with {json}\n"
                    f"{response.status_code} {response.text}")
            command.id = response.json()["id"]

    def add_slash_command(self, command, app=None, name=None,
                          description=None, options=[]):
        if not 3 <= len(name) <= 32:
            raise ValueError(
                f"Error adding command {name}: "
                "Command name must be between 3 and 32 characters.")
        if not 1 <= len(description) <= 100:
            raise ValueError(
                f"Error adding command {name}: "
                "Command description must be between 1 and 100 characters.")
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
