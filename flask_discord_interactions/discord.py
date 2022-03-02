import time
import inspect
import uuid
import atexit
import asyncio
import warnings

import requests

from flask import current_app, request, jsonify, abort

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from flask_discord_interactions.models.autocomplete import AutocompleteResult

try:
    import aiohttp
except ImportError:
    aiohttp = None

from flask_discord_interactions.command import Command, SlashCommandGroup
from flask_discord_interactions.context import Context, ApplicationCommandType
from flask_discord_interactions.models import Message, Modal, ResponseType


class InteractionType:
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class DiscordInteractionsBlueprint:
    """
    Represents a collection of :class:`ApplicationCommand` s.

    Useful for splitting a bot across multiple files.
    """

    def __init__(self):
        self.discord_commands = {}
        self.custom_id_handlers = {}
        self.autocomplete_handlers = {}

    def add_command(
        self,
        command,
        name=None,
        description=None,
        options=None,
        annotations=None,
        type=ApplicationCommandType.CHAT_INPUT,
        default_permission=None,
        permissions=None,
    ):
        """
        Create and add a new :class:`ApplicationCommand`.

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
        type
            The ``ApplicationCommandType`` of the command.
        default_permission
            Whether the command is enabled by default. Default is True.
        permissions
            List of permission overwrites.
        """
        command = Command(
            command,
            name,
            description,
            options,
            annotations,
            type,
            default_permission,
            permissions,
            self,
        )
        self.discord_commands[command.name] = command
        return command

    def add_slash_command(self, *args, **kwargs):
        """
        Deprecated! As of v1.1.0, ``add_slash_command`` has been renamed to
        :meth:`add_command`, as it can now add User and Message commands.
        """
        warnings.warn(
            "Deprecated! As of v1.1.0, add_slash_command has been renamed to "
            "add_command, as it can now add User and Message commands.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.add_command(*args, **kwargs)

    def command(
        self,
        name=None,
        description=None,
        options=None,
        annotations=None,
        type=ApplicationCommandType.CHAT_INPUT,
        default_permission=None,
        permissions=None,
    ):
        """
        Decorator to create a new :class:`Command`.

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
        type
            The ``ApplicationCommandType`` of the command.
        default_permission
            Whether the command is enabled by default. Default is True.
        permissions
            List of permission overwrites.
        """

        def decorator(func):
            nonlocal name, description, type, options
            command = self.add_command(
                func,
                name,
                description,
                options,
                annotations,
                type,
                default_permission,
                permissions,
            )
            return command

        return decorator

    def command_group(
        self,
        name,
        description="No description",
        is_async=False,
        default_permission=None,
        permissions=None,
    ):
        """
        Create a new :class:`SlashCommandGroup`
        (which can contain multiple subcommands)

        Parameters
        ----------
        name
            The name of the command group, as displayed in the Discord client.
        description
            The description of the command group.
        is_async
            Whether the subgroup should be considered async (if subcommands
            get an :class:`.AsyncContext` instead of a :class:`Context`.)
        default_permission
            Whether the command group is enabled by default.
        permissions
            List of permission overwrites. These apply to the entire group.
        """

        group = SlashCommandGroup(
            name, description, is_async, default_permission, permissions
        )
        self.discord_commands[name] = group
        return group

    def add_custom_handler(self, handler, custom_id=None):
        """
        Add a handler for an incoming interaction with the specified custom ID.

        Parameters
        ----------
        handler
            The function to call to handle the incoming interaction.
        custom_id
            The custom ID to respond to. If not specified, the ID will be
            generated randomly.

        Returns
        -------
        str
            The custom ID that the handler will respond to.
        """
        if custom_id is None:
            custom_id = str(uuid.uuid4())

        self.custom_id_handlers[custom_id] = handler
        return custom_id

    def custom_handler(self, custom_id=None):
        """
        Returns a decorator to register a handler for a custom ID.

        Parameters
        ----------
        custom_id
            The custom ID to respond to. If not specified, the ID will be
            generated randomly.
        """

        def decorator(func):
            nonlocal custom_id
            custom_id = self.add_custom_handler(func, custom_id)
            return custom_id

        return decorator

    def add_autocomplete_handler(self, handler, command_name):
        """
        Add a handler for an incoming autocomplete request.

        Parameters
        ----------
        handler
            The function to call to handle the incoming autocomplete request.
        command_name
            The name of the command to autocomplete.
        """
        self.autocomplete_handlers[command_name] = handler


class DiscordInteractions(DiscordInteractionsBlueprint):
    """
    Handles registering a collection of :class:`Command` s, receiving
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

        app.config.setdefault("DISCORD_BASE_URL", "https://discord.com/api/v9")
        app.config.setdefault("DISCORD_CLIENT_ID", "")
        app.config.setdefault("DISCORD_PUBLIC_KEY", "")
        app.config.setdefault("DISCORD_CLIENT_SECRET", "")
        app.config.setdefault("DONT_VALIDATE_SIGNATURE", False)
        app.config.setdefault("DONT_REGISTER_WITH_DISCORD", False)
        app.discord_commands = self.discord_commands
        app.custom_id_handlers = self.custom_id_handlers
        app.autocomplete_handlers = self.autocomplete_handlers
        app.discord_token = None

    def fetch_token(self, app=None):
        """
        Fetch an OAuth2 token from Discord using the ``CLIENT_ID`` and
        ``CLIENT_SECRET`` with the ``applications.commands.update`` scope. This
        can be used to register new application commands.

        Parameters
        ----------
        app
            The Flask app with the relevant config (client ID and secret).
        """

        if app is None:
            app = self.app

        if app.config["DONT_REGISTER_WITH_DISCORD"]:
            app.discord_token = {
                "token_type": "Bearer",
                "scope": "applications.commands.update",
                "expires_in": 604800,
                "access_token": "DONT_REGISTER_WITH_DISCORD",
            }
            app.discord_token["expires_on"] = (
                time.time() + app.discord_token["expires_in"] / 2
            )
            return
        response = requests.post(
            app.config["DISCORD_BASE_URL"] + "/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "scope": "applications.commands.update",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=(app.config["DISCORD_CLIENT_ID"], app.config["DISCORD_CLIENT_SECRET"]),
        )

        response.raise_for_status()
        app.discord_token = response.json()
        app.discord_token["expires_on"] = (
            time.time() + app.discord_token["expires_in"] / 2
        )

    def auth_headers(self, app):
        """
        Get the Authorization header required for HTTP requests to the
        Discord API.

        Parameters
        ----------
        app
            The Flask app with the relevant access token.
        """

        if app.discord_token is None or time.time() > app.discord_token["expires_on"]:
            self.fetch_token(app)
        return {"Authorization": f"Bearer {app.discord_token['access_token']}"}

    def update_commands(self, app=None, guild_id=None):
        """
        Update the list of commands registered with Discord.
        This method will overwrite all existing commands.

        Make sure you aren't calling this every time a new worker starts! You
        will run into rate-limiting issues if multiple workers attempt to
        register commands simultaneously. Read :ref:`workers` for more
        info.

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

        if guild_id:
            url = (
                f"{app.config['DISCORD_BASE_URL']}/applications/"
                f"{app.config['DISCORD_CLIENT_ID']}/"
                f"guilds/{guild_id}/commands"
            )
        else:
            url = (
                f"{app.config['DISCORD_BASE_URL']}/applications/"
                f"{app.config['DISCORD_CLIENT_ID']}/commands"
            )

        overwrite_data = [command.dump() for command in app.discord_commands.values()]

        if not app.config["DONT_REGISTER_WITH_DISCORD"]:
            response = requests.put(
                url, json=overwrite_data, headers=self.auth_headers(app)
            )
            self.throttle(response)

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                raise ValueError(
                    f"Unable to register commands:"
                    f"{response.status_code} {response.text}"
                )

            for command in response.json():
                if command["name"] in app.discord_commands:
                    app.discord_commands[command["name"]].id = command["id"]
        else:
            for command in app.discord_commands.values():
                command.id = command.name

        url += "/permissions"

        permissions_data = [
            {"id": command.id, "permissions": command.dump_permissions()}
            for command in app.discord_commands.values()
            if command.permissions
        ]

        if not permissions_data:
            return

        if not app.config["DONT_REGISTER_WITH_DISCORD"]:
            response = requests.put(
                url, json=permissions_data, headers=self.auth_headers(app)
            )
            self.throttle(response)

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                raise ValueError(
                    f"Unable to register permissions:"
                    f"{response.status_code} {response.text}"
                )

    def update_slash_commands(self, *args, **kwargs):
        """
        Deprecated! As of v1.1.0, ``update_slash_commands`` has been renamed to
        ``update_commands``, as it updates User and Message commands as well.
        """
        warnings.warn(
            "Deprecated! As of v1.1.0, update_slash_commands has been renamed "
            "to update_commands, as it updates User and Message commands too.",
            DeprecationWarning,
            stacklevel=2,
        )

        return self.update_commands(*args, **kwargs)

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
            time.sleep(max(rate_limit_reset - time.time(), 0))

    def register_blueprint(self, blueprint, app=None):
        """
        Register a :class:`DiscordInteractionsBlueprint` to this
        DiscordInteractions class. Updates this instance's list of
        :class:`Command` s using the blueprint's list of
        :class:`Command` s.

        Parameters
        ----------
        blueprint
            The :class:`DiscordInteractionsBlueprint` to add
            :class:`Command` s from.
        app
            The Flask app with the relevant Discord commands.
        """

        if app is None:
            app = self.app

        app.discord_commands.update(blueprint.discord_commands)
        app.custom_id_handlers.update(blueprint.custom_id_handlers)
        app.autocomplete_handlers.update(blueprint.autocomplete_handlers)

    def run_command(self, data):
        """
        Run the corresponding :class:`Command` given incoming interaction
        data.

        Parameters
        ----------
        data
            Incoming interaction data.
        """

        command_name = data["data"]["name"]

        command = current_app.discord_commands.get(command_name)

        if command is None:
            raise ValueError(f"Invalid command name: {command_name}")

        return command.make_context_and_run(self, current_app, data)

    def run_handler(self, data, *, allow_modal=True):
        """
        Run the corresponding custom ID handler given incoming interaction
        data.

        Parameters
        ----------
        data
            Incoming interaction data.
        """

        context = Context.from_data(self, current_app, data)
        handler = self.custom_id_handlers[context.primary_id]
        args = context.create_handler_args(handler)
        result = handler(context, *args)

        if isinstance(result, Modal):
            if allow_modal:
                return result
            else:
                raise ValueError("Cannot return a Modal to that interaction type.")

        return Message.from_return_value(result)

    def run_autocomplete(self, data):
        """
        Run the corresponding autocomplete handler given incoming interaction
        data.

        Parameters
        ----------
        data
            Incoming interaction data.
        """

        context = Context.from_data(self, current_app, data)
        handler = self.autocomplete_handlers[context.command_name]
        args = context.create_autocomplete_args()
        result = handler(context, *args)

        return AutocompleteResult.from_return_value(result)

    def verify_signature(self, request):
        """
        Verify the signature sent by Discord with incoming interactions.

        Parameters
        ----------
        request
            The request to verify the signature of.
        """

        signature = request.headers.get("X-Signature-Ed25519")
        timestamp = request.headers.get("X-Signature-Timestamp")

        if current_app.config["DONT_VALIDATE_SIGNATURE"]:
            return

        if signature is None or timestamp is None:
            abort(401, "Missing signature or timestamp")

        message = timestamp.encode() + request.data
        verify_key = VerifyKey(bytes.fromhex(current_app.config["DISCORD_PUBLIC_KEY"]))
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

        If you are using Quart, you should use
        :meth:`.DiscordInteractions.set_route_async` instead.

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

            interaction_type = request.json.get("type")
            if interaction_type == InteractionType.PING:
                return jsonify({"type": ResponseType.PONG})

            elif interaction_type == InteractionType.APPLICATION_COMMAND:
                return jsonify(self.run_command(request.json).dump())

            elif interaction_type == InteractionType.MESSAGE_COMPONENT:
                return jsonify(self.run_handler(request.json).dump_handler())

            elif interaction_type == InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE:
                return jsonify(self.run_autocomplete(request.json).dump())

            elif interaction_type == InteractionType.MODAL_SUBMIT:
                return jsonify(self.run_handler(request.json, allow_modal=False).dump_handler())

            else:
                raise RuntimeWarning(
                    f"Interaction type {interaction_type} is not yet supported"
                )

    def set_route_async(self, route, app=None):
        """
        Add a route handler to a Quart app that handles incoming interaction
        data using asyncio.

        This function also sets up the aiohttp ClientSession that is used
        for sending followup messages, etc.

        Parameters
        ----------
        route
            The URL path to receive interactions on.
        app
            The Flask app to add the route to.
        """

        if app is None:
            app = self.app

        if aiohttp is None:
            raise ImportError(
                "The aiohttp module is required for async usage of this " "library"
            )

        @app.route(route, methods=["POST"])
        async def interactions():
            self.verify_signature(request)

            interaction_type = request.json.get("type")
            if interaction_type == InteractionType.PING:
                return jsonify({"type": ResponseType.PONG})

            elif interaction_type == InteractionType.APPLICATION_COMMAND:
                result = self.run_command(request.json)
            elif interaction_type == InteractionType.MESSAGE_COMPONENT:
                result = self.run_handler(request.json)
            elif interaction_type == InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE:
                result = self.run_autocomplete(request.json)

            elif interaction_type == InteractionType.MODAL_SUBMIT:
                result = self.run_handler(request.json, allow_modal=False)

            else:
                raise RuntimeWarning(
                    f"Interaction type {interaction_type} is not yet supported"
                )

            if inspect.isawaitable(result):
                result = await result

            return jsonify(result.dump())

        # Set up the aiohttp ClientSession

        async def create_session():
            app.discord_client_session = aiohttp.ClientSession(
                headers=self.auth_headers(app), raise_for_status=True
            )

        async def close_session():
            await app.discord_client_session.close()

        if hasattr(app, "before_serving"):
            # Quart apps
            app.before_serving(create_session)
            app.after_serving(close_session)
        else:
            # Flask apps
            app.before_first_request(create_session)
            atexit.register(
                lambda: asyncio.get_event_loop().run_until_complete(close_session())
            )
