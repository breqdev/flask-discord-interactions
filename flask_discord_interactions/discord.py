import time
import inspect

import requests

from flask import current_app, request, jsonify, abort

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from flask_discord_interactions.command import SlashCommand, SlashCommandGroup
from flask_discord_interactions.response import ResponseType


class InteractionType:
    PING = 1
    APPLICATION_COMMAND = 2


class DiscordInteractionsBlueprint:
    """
    Represents a collection of :class:`SlashCommand` s.

    Useful for splitting a bot across multiple files.
    """
    def __init__(self):
        self.discord_commands = {}

    def add_slash_command(self, command, name=None,
                          description=None, options=None, annotations=None):
        """
        Create and add a new :class:`SlashCommand`.

        Parameters
        ----------
        command
            Function to execute when the command is run.
        name
            The name of the command, as displayed in the Discord client.
        description
            The description of the command.
        options
            A list of options for the command, overriding the function's
            keyword arguments.
        annotations
            If ``options`` is not provided, descriptions for each of the
            options defined in the function's keyword arguments.
        """
        slash_command = SlashCommand(
            command, name, description, options, annotations)
        self.discord_commands[slash_command.name] = slash_command

    def command(self, name=None, description=None,
                options=None, annotations=None):
        """
        Decorator to create a new :class:`SlashCommand`.

        Parameters
        ----------
        name
            The name of the command, as displayed in the Discord client.
        description
            The description of the command.
        options
            A list of options for the command, overriding the function's
            keyword arguments.
        annotations
            If ``options`` is not provided, descriptions for each of the
            options defined in the function's keyword arguments.
        """

        def decorator(func):
            nonlocal name, description, options
            self.add_slash_command(
                func, name, description, options, annotations)
            return func

        return decorator

    def command_group(self, name, description="No description"):
        """
        Create a new :class:`SlashCommandGroup`
        (which can contain multiple subcommands)

        Parameters
        ----------
        name
            The name of the command group, as displayed in the Discord client.
        description
            The description of the command group.
        """
        group = SlashCommandGroup(name, description)
        self.discord_commands[name] = group
        return group


class DiscordInteractions(DiscordInteractionsBlueprint):
    """
    Handles registering a collection of :class:`SlashCommand` s, receiving
    incoming interaction data, and sending/editing/deleting messages via
    webhook.
    """
    def __init__(self, app=None):
        super().__init__()

        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize a Flask app with Discord-specific configuration and
        attributes.

        Parameters
        ----------
        app
            The Flask app to initialize.
        """

        app.config.setdefault("DISCORD_CLIENT_ID", "")
        app.config.setdefault("DISCORD_PUBLIC_KEY", "")
        app.config.setdefault("DISCORD_CLIENT_SECRET", "")
        app.config.setdefault("DONT_VALIDATE_SIGNATURE", False)
        app.config.setdefault("DONT_REGISTER_WITH_DISCORD", False)
        app.discord_commands = self.discord_commands
        app.discord_token = None

    def fetch_token(self, app=None):
        """
        Fetch an OAuth2 token from Discord using the ``CLIENT_ID`` and
        ``CLIENT_SECRET`` with the ``applications.commands.update`` scope. This
        can be used to register new slash commands.

        Parameters
        ----------
        app
            The Flask app with the relevant config (client ID and secret).
        """

        if app is None:
            app = self.app

        if app.config['DONT_REGISTER_WITH_DISCORD']:
            app.discord_token = {
                'token_type':'Bearer',
                'scope':'applications.commands.update',
                'expires_in':604800,
                'access_token':'DONT_REGISTER_WITH_DISCORD'
            }
            app.discord_token["expires_on"] = (time.time() + app.discord_token["expires_in"]/2)
            return
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
        app.discord_token = response.json()
        app.discord_token["expires_on"] = (time.time()
                                           + app.discord_token["expires_in"]/2)

    def auth_headers(self, app):
        """
        Get the Authorization header required for HTTP requests to the
        Discord API.

        Parameters
        ----------
        app
            The Flask app with the relevant access token.
        """

        if (app.discord_token is None
                or time.time() > app.discord_token["expires_on"]):
            self.fetch_token(app)
        return {"Authorization": f"Bearer {app.discord_token['access_token']}"}

    def update_slash_commands(self, app=None, guild_id=None):
        """
        Update the list of slash commands registered with Discord.
        This method will delete old/unused slash commands, update modified
        slash commands, and register new slash commands.

        Parameters
        ----------
        app
            The Flask app with the relevant Discord access token.
        guild_id
            The ID of the Discord guild to register commands to. If omitted,
            the commands are registered globally.
        """

        if app is None:
            app = self.app

        if app.config['DONT_REGISTER_WITH_DISCORD']:
            return

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
            self.throttle(response)
            response.raise_for_status()

        for name, command in needed.items():
            response = requests.post(
                url, json=command.dump(), headers=self.auth_headers(app))
            self.throttle(response)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                raise ValueError(
                    f"Unable to register command {command.name}\n"
                    f"{response.status_code} {response.text}")
            command.id = response.json()["id"]

    def throttle(self, response):
        """
        Throttle the number of HTTP requests made to Discord
        using the ``X-RateLimit`` headers
        https://discord.com/developers/docs/topics/rate-limits

        Parameters
        ----------
        response
            Response object from a previous HTTP request
        """

        rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])
        rate_limit_reset = float(response.headers["X-RateLimit-Reset"])
        # rate_limit_limit = response.headers["X-RateLimit-Limit"]
        # rate_limit_bucket = response.headers["X-RateLimit-Bucket"]

        if not rate_limit_remaining:
            time.sleep(rate_limit_reset - time.time())

    def register_blueprint(self, blueprint, app=None):
        """
        Register a :class:`DiscordInteractionsBlueprint` to this
        iscordInteractions class. Updates this instance's list of
        :class:`SlashCommand` s using the blueprint's list of
        :class:`SlashCommand` s.

        Parameters
        ----------
        blueprint
            The :class:`DiscordInteractionsBlueprint` to add
            :class:`SlashCommand` s from.
        app
            The Flask app with the relevant Discord commands.
        """

        if app is None:
            app = self.app

        app.discord_commands.update(blueprint.discord_commands)

    def run_command(self, data):
        """
        Run the corresponding :class:`SlashCommand` given incoming interaction
        data.

        Parameters
        ----------
        data
            Incoming interaction data.
        """

        command_name = data["data"]["name"]

        slash_command = current_app.discord_commands.get(command_name)

        if slash_command is None:
            raise ValueError(f"Invalid command name: {command_name}")

        return slash_command.make_context_and_run(self, current_app, data)

    def verify_signature(self, request):
        """
        Verify the signature sent by Discord with incoming interactions.

        Parameters
        ----------
        request
            The request to verify the signature of.
        """

        signature = request.headers.get('X-Signature-Ed25519')
        timestamp = request.headers.get('X-Signature-Timestamp')

        if current_app.config["DONT_VALIDATE_SIGNATURE"]:
            return

        if signature is None or timestamp is None:
            abort(401, "Missing signature or timestamp")

        message = timestamp.encode() + request.data
        verify_key = VerifyKey(
            bytes.fromhex(current_app.config["DISCORD_PUBLIC_KEY"]))
        try:
            verify_key.verify(message, bytes.fromhex(signature))
        except BadSignatureError:
            abort(401, "Incorrect Signature")

        if not request.json:
            abort(400, "Request JSON required")


    def set_route(self, route, app=None):
        """
        Add a route handler to the Flask app that handles incoming
        interaction data.

        Parameters
        ----------
        route
            The URL path to receive interactions on.
        app
            The Flask app to add the route to.
        """

        if app is None:
            app = self.app

        @app.route(route, methods=["POST"])
        def interactions():
            self.verify_signature(request)

            if request.json.get("type") == InteractionType.PING:
                return jsonify({"type": ResponseType.PONG})

            return jsonify(self.run_command(request.json).dump())

    def set_route_async(self, route, app=None):
        """
        Add a route handler to a Quart app that handles incoming interaction
        data using asyncio.

        Parameters
        ----------
        route
            The URL path to receive interactions on.
        app
            The Flask app to add the route to.
        """

        if app is None:
            app = self.app

        @app.route(route, methods=["POST"])
        async def interactions():
            self.verify_signature(request)

            if request.json.get("type") == InteractionType.PING:
                return jsonify({"type": ResponseType.PONG})

            result = self.run_command(request.json)
            if inspect.isawaitable(result):
                result = await result

            return jsonify(result.dump())
