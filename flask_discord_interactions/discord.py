import time
import inspect
from typing import Callable, Dict, List
import uuid
import atexit
import asyncio
import warnings

import requests

from flask import Flask, Response, current_app, request, jsonify, abort

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from flask_discord_interactions.models.autocomplete import AutocompleteResult
from flask_discord_interactions.models.option import Option

try:
    import aiohttp
except ImportError:
    aiohttp = None

from flask_discord_interactions.command import Command, SlashCommandGroup
from flask_discord_interactions.context import Context, ApplicationCommandType
from flask_discord_interactions.models import Message, Modal, ResponseType, Permission
from flask_discord_interactions.utils import static_or_instance


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
        command: Callable,
        name: str = None,
        description: str = None,
        *,
        options: List[Option] = None,
        annotations: Dict[str, str] = None,
        type: int = ApplicationCommandType.CHAT_INPUT,
        default_member_permissions: int = None,
        dm_permission: bool = None,
        name_localizations: Dict[str, str] = None,
        description_localizations: Dict[str, str] = None,
    ):
        """
        Create and add a new :class:`ApplicationCommand`.

        Parameters
        ----------
        command: Callable
            Function to execute when the command is run.
        name: str
            The name of the command, as displayed in the Discord client.
        name_localizations: Dict[str, str]
            A dictionary of localizations for the name of the command.
        description: str
            The description of the command.
        description_localizations: Dict[str, str]
            A dictionary of localizations for the description of the command.
        options: List[Option]
            A list of options for the command, overriding the function's
            keyword arguments.
        annotations: Dict[str, str]
            If ``options`` is not provided, descriptions for each of the
            options defined in the function's keyword arguments.
        type: int
            The class:`.ApplicationCommandType` of the command.
        default_member_permissions: int
            A permission integer defining the required permissions a user must have to run the command.
        dm_permission: bool
            Indicates whether the command can be used in DMs.
        """
        command = Command(
            command=command,
            name=name,
            description=description,
            options=options,
            annotations=annotations,
            type=type,
            default_member_permissions=default_member_permissions,
            dm_permission=dm_permission,
            name_localizations=name_localizations,
            description_localizations=description_localizations,
            discord=self,
        )
        self.discord_commands[command.name] = command
        return command

    def command(
        self,
        name: str = None,
        description: str = None,
        *,
        options: List[Option] = None,
        annotations: Dict[str, str] = None,
        type: int = ApplicationCommandType.CHAT_INPUT,
        default_member_permissions: int = None,
        dm_permission: bool = None,
        name_localizations: Dict[str, str] = None,
        description_localizations: Dict[str, str] = None,
    ):
        """
        Decorator to create a new :class:`Command`.

        Parameters
        ----------
        name: str
            The name of the command, as displayed in the Discord client.
        name_localizations: Dict[str, str]
            A dictionary of localizations for the name of the command.
        description: str
            The description of the command.
        description_localizations: Dict[str, str]
            A dictionary of localizations for the description of the command.
        options: List[Option]
            A list of options for the command, overriding the function's
            keyword arguments.
        annotations: Dict[str, str]
            If ``options`` is not provided, descriptions for each of the
            options defined in the function's keyword arguments.
        type: int
            The ``ApplicationCommandType`` of the command.
        default_member_permissions: int
            A permission integer defining the required permissions a user must have to run the command
        dm_permission: bool
            Indicates whether the command can be used in DMs

        Returns
        -------
        Callable[Callable, Command]
        """

        def decorator(func):
            nonlocal name, description, type, options
            command = self.add_command(
                func,
                name=name,
                description=description,
                options=options,
                annotations=annotations,
                type=type,
                default_member_permissions=default_member_permissions,
                dm_permission=dm_permission,
                name_localizations=name_localizations,
                description_localizations=description_localizations,
            )
            return command

        return decorator

    def command_group(
        self,
        name: str,
        description: str = "No description",
        *,
        is_async: bool = False,
        default_member_permissions: int = None,
        dm_permission: bool = None,
        name_localizations: Dict[str, str] = None,
        description_localizations: Dict[str, str] = None,
    ):
        """
        Create a new :class:`SlashCommandGroup`
        (which can contain multiple subcommands)

        Parameters
        ----------
        name: str
            The name of the command group, as displayed in the Discord client.
        name_localizations: Dict[str, str]
            A dictionary of localizations for the name of the command group.
        description: str
            The description of the command group.
        description_localizations: Dict[str, str]
            A dictionary of localizations for the description of the command group.
        is_async: bool
            Whether the subgroup should be considered async (if subcommands
            get an :class:`.AsyncContext` instead of a :class:`Context`.)
        default_member_permissions: int
            A permission integer defining the required permissions a user must have to run the command
        dm_permission: bool
            Indicates whether the command canbe used in DMs

        Returns
        -------
        SlashCommandGroup
            The newly created command group.
        """

        group = SlashCommandGroup(
            name=name,
            description=description,
            is_async=is_async,
            default_member_permissions=default_member_permissions,
            dm_permission=dm_permission,
            name_localizations=name_localizations,
            description_localizations=description_localizations,
        )
        self.discord_commands[name] = group
        return group

    def add_custom_handler(self, handler: Callable, custom_id: str = None):
        """
        Add a handler for an incoming interaction with the specified custom ID.

        Parameters
        ----------
        handler: Callable
            The function to call to handle the incoming interaction.
        custom_id: str
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

    def custom_handler(self, custom_id: str = None):
        """
        Returns a decorator to register a handler for a custom ID.

        Parameters
        ----------
        custom_id
            The custom ID to respond to. If not specified, the ID will be
            generated randomly.

        Returns
        -------
        Callable[Callable, str]
        """

        def decorator(func):
            nonlocal custom_id
            custom_id = self.add_custom_handler(func, custom_id)
            return custom_id

        return decorator

    def add_autocomplete_handler(self, handler: Callable, command_name: str):
        """
        Add a handler for an incoming autocomplete request.

        Parameters
        ----------
        handler: Callable
            The function to call to handle the incoming autocomplete request.
        command_name: str
            The name of the command to autocomplete.
        """
        self.autocomplete_handlers[command_name] = handler


class DiscordInteractions(DiscordInteractionsBlueprint):
    """
    Handles registering a collection of :class:`Command` s, receiving
    incoming interaction data, and sending/editing/deleting messages via
    webhook.

    Parameters
    ----------
    app: Flask
        The Flask application to bind to.
    """

    def __init__(self, app: Flask = None):
        super().__init__()

        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initialize a Flask app with Discord-specific configuration and
        attributes.

        Parameters
        ----------
        app: Flask
            The Flask app to initialize.
        """

        app.config.setdefault("DISCORD_BASE_URL", "https://discord.com/api/v10")
        app.config.setdefault("DISCORD_CLIENT_ID", "")
        app.config.setdefault("DISCORD_PUBLIC_KEY", "")
        app.config.setdefault("DISCORD_CLIENT_SECRET", "")
        app.config.setdefault("DISCORD_SCOPE", "applications.commands.update")
        app.config.setdefault("DONT_VALIDATE_SIGNATURE", False)
        app.config.setdefault("DONT_REGISTER_WITH_DISCORD", False)
        app.discord_commands = self.discord_commands
        app.custom_id_handlers = self.custom_id_handlers
        app.autocomplete_handlers = self.autocomplete_handlers
        app.discord_token = None

    @static_or_instance
    def fetch_token(self, app: Flask = None):
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
                "scope": app.config["DISCORD_SCOPE"],
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
                "scope": app.config["DISCORD_SCOPE"],
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=(app.config["DISCORD_CLIENT_ID"], app.config["DISCORD_CLIENT_SECRET"]),
        )

        response.raise_for_status()
        app.discord_token = response.json()
        app.discord_token["expires_on"] = (
            time.time() + app.discord_token["expires_in"] / 2
        )

    @staticmethod
    def auth_headers(app: Flask):
        """
        Get the Authorization header required for HTTP requests to the
        Discord API.

        Parameters
        ----------
        app: Flask
            The Flask app with the relevant access token.

        Returns
        -------
        Dict[str, str]
            The Authorization header.
        """

        if app.discord_token is None or time.time() > app.discord_token["expires_on"]:
            DiscordInteractions.fetch_token(app)
        return {"Authorization": f"Bearer {app.discord_token['access_token']}"}

    def update_commands(self, app: Flask = None, guild_id: str = None):
        """
        Update the list of commands registered with Discord.
        This method will overwrite all existing commands.

        Make sure you aren't calling this every time a new worker starts! You
        will run into rate-limiting issues if multiple workers attempt to
        register commands simultaneously. Read :ref:`workers` for more
        info.

        Parameters
        ----------
        app: Flask
            The Flask app with the relevant Discord access token.
        guild_id: str
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

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                raise ValueError(
                    f"Unable to register commands:"
                    f"{response.status_code} {response.text}"
                )

            self.throttle(response)

            for command in response.json():
                if command["name"] in app.discord_commands:
                    app.discord_commands[command["name"]].id = command["id"]
        else:
            for command in app.discord_commands.values():
                command.id = command.name

    @staticmethod
    def build_permission_overwrite_url(
        self,
        command: Command = None,
        *,
        guild_id: str,
        command_id: str = None,
        token: str = None,
        app: Flask = None,
        application_id: str = None,
        base_url: str = None,
    ):
        """
        Build the URL for getting or setting permission overwrites for a
        specific guild and command.
        """
        if not app and self and self.app:
            app = self.app

        if not application_id or not base_url:
            if app:
                application_id = app.config["DISCORD_CLIENT_ID"]
                base_url = app.config["DISCORD_BASE_URL"]
            else:
                raise ValueError(
                    "This method requires the application ID and base URL."
                    " Either provide these as arguments or provide an app "
                    " instance with the relevant configuration."
                )

        if command_id is None:
            if command:
                command_id = command.id
            else:
                raise ValueError(
                    "You must supply either a command ID or a Command instance."
                )

        url = f"{base_url}/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions"
        auth = (
            {"Authorization": f"Bearer {token}"}
            if token
            else DiscordInteractions.auth_headers(app)
        )

        return url, auth

    @static_or_instance
    def get_permission_overwrites(
        self,
        command: Command = None,
        *,
        guild_id: str,
        command_id: str = None,
        token: str = None,
        app: Flask = None,
        application_id: str = None,
        base_url: str = None,
    ):
        """
        Get the list of permission overwrites in a specific guild for a
        specific command. You must supply a Bearer token from a user with
        "Manage Roles" and "Manage Server" permissions in the given guild.

        If the token is omitted, the bot's token will be used. Note that this
        only works if the bot's developer account is an admin in the guild.
        This is handy for small bots on your own servers, but you shouldn't
        rely on this for anything you want others to use in their servers.

        There are a many ways to call this method, here are a few:

        .. code-block:: python

            # Without the app or instance, useful in a background worker
            DiscordInteractions.get_permission_overwrites(
                guild_id=...,
                command_id=...,
                token=...,
                application_id=...,
                base_url=...,
            )

            # With the instance and app passed in, useful in an app-factory project
            discord.get_permission_overwrites(
                guild_id=...,
                command=...,
                token=...,
                app=...,
            )

            # With the instance and a bound app, using an implicit token
            # useful in most small projects
            discord.get_permission_overwrites(
                guild_id=...,
                command=...,
            )

        Parameters
        ----------
        command: Command
            The :class:`.Command` to retrieve permissions for.
        guild_id: str
            The ID of the guild to retrieve permissions from.
        command_id: str
            The ID of the command to retrieve permissions for.
        token: str
            A bearer token from an admin of the guild (not including the
            leading ``Bearer`` word). If omitted, the bot's token will be
            used instead.
        app: Flask
            The Flask app with the relevant Discord application ID.
        application_id: str
            The ID of the Discord application to retrieve permissions from.
        base_url: str
            The base URL of the Discord API.

        Returns
        -------
        List[Permission]
            A list of permission overwrites for the given command.
        """

        url, auth = DiscordInteractions.build_permission_overwrite_url(
            self,
            command,
            guild_id=guild_id,
            command_id=command_id,
            token=token,
            app=app,
            application_id=application_id,
            base_url=base_url,
        )

        response = requests.get(
            url,
            headers=auth,
        )
        response.raise_for_status()

        return [Permission.from_dict(perm) for perm in response.json()]

    @static_or_instance
    def set_permission_overwrites(
        self,
        permissions: List[Permission],
        command: Command = None,
        *,
        guild_id: str,
        command_id: str = None,
        token: str = None,
        app: Flask = None,
        application_id: str = None,
        base_url: str = None,
    ):
        """
        Overwrite the list of permission overwrites in a specific guild for a
        specific command. You must supply a Bearer token from a user with
        "Manage Roles" and "Manage Server" permissions in the given guild.

        This method requires access to the application ID and base URL. For
        convenience, it can be called as either an instance method (using the
        bound app's configuration) or a static method.

        Parameters
        ----------
        command: Command
            The :class:`.Command` to retrieve permissions for.
        guild_id: str
            The ID of the guild to retrieve permissions from.
        command_id: str
            The ID of the command to retrieve permissions for.
        token: str
            A bearer token from an admin of the guild (not including the
            leading ``Bearer`` word). If omitted, the bot's token will be
            used instead.
        app: Flask
            The Flask app with the relevant Discord application ID.
        application_id: str
            The ID of the Discord application to retrieve permissions from.
        base_url: str
            The base URL of the Discord API.
        """

        url, auth = DiscordInteractions.build_permission_overwrite_url(
            self,
            command,
            guild_id=guild_id,
            command_id=command_id,
            token=token,
            app=app,
            application_id=application_id,
            base_url=base_url,
        )

        response = requests.put(
            url,
            headers=auth,
            json={"permissions": [perm.dump() for perm in permissions]},
        )
        response.raise_for_status()

    def throttle(self, response: requests.Response):
        """
        Throttle the number of HTTP requests made to Discord
        using the ``X-RateLimit`` headers
        https://discord.com/developers/docs/topics/rate-limits

        Parameters
        ----------
        response: requests.Response
            Response object from a previous HTTP request
        """

        rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])
        rate_limit_reset = float(response.headers["X-RateLimit-Reset"])
        # rate_limit_limit = response.headers["X-RateLimit-Limit"]
        # rate_limit_bucket = response.headers["X-RateLimit-Bucket"]

        if not rate_limit_remaining:
            wait_time = rate_limit_reset - time.time()
            warnings.warn(
                f"You are being rate limited. Waiting {int(wait_time)} seconds..."
            )
            time.sleep(max(wait_time, 0))

    def register_blueprint(
        self, blueprint: DiscordInteractionsBlueprint, app: Flask = None
    ):
        """
        Register a :class:`DiscordInteractionsBlueprint` to this
        DiscordInteractions class. Updates this instance's list of
        :class:`Command` s using the blueprint's list of
        :class:`Command` s.

        Parameters
        ----------
        blueprint: DiscordInteractionsBlueprint
            The :class:`DiscordInteractionsBlueprint` to add
            :class:`Command` s from.
        app: Flask
            The Flask app with the relevant Discord commands.
        """

        if app is None:
            app = self.app

        app.discord_commands.update(blueprint.discord_commands)
        app.custom_id_handlers.update(blueprint.custom_id_handlers)
        app.autocomplete_handlers.update(blueprint.autocomplete_handlers)

    def run_command(self, data: dict):
        """
        Run the corresponding :class:`Command` given incoming interaction
        data.

        Parameters
        ----------
        data
            Incoming interaction data.

        Returns
        -------
        Message
            The resulting message from the command.
        """

        command_name = data["data"]["name"]

        command = current_app.discord_commands.get(command_name)

        if command is None:
            raise ValueError(f"Invalid command name: {command_name}")

        return command.make_context_and_run(discord=self, app=current_app, data=data)

    def run_handler(self, data: dict, *, allow_modal: bool = True):
        """
        Run the corresponding custom ID handler given incoming interaction
        data.

        Parameters
        ----------
        data
            Incoming interaction data.

        Returns
        -------
        Message
            The resulting message.
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

    def run_autocomplete(self, data: dict):
        """
        Run the corresponding autocomplete handler given incoming interaction
        data.

        Parameters
        ----------
        data
            Incoming interaction data.

        Returns
        -------
        AutocompleteResult
            The result of the autocomplete handler.
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

    def handle_request(self):
        """
        Verify the signature in the incoming request and return the Message
        result from the given command.

        Returns
        -------
        Message
            The resulting message from the command.
        """
        self.verify_signature(request)

        interaction_type = request.json.get("type")
        if interaction_type == InteractionType.PING:
            abort(jsonify({"type": ResponseType.PONG}))
        elif interaction_type == InteractionType.APPLICATION_COMMAND:
            return self.run_command(request.json)
        elif interaction_type == InteractionType.MESSAGE_COMPONENT:
            return self.run_handler(request.json)
        elif interaction_type == InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE:
            return self.run_autocomplete(request.json)
        elif interaction_type == InteractionType.MODAL_SUBMIT:
            return self.run_handler(request.json, allow_modal=False)
        else:
            raise RuntimeWarning(
                f"Interaction type {interaction_type} is not yet supported"
            )

    def set_route(self, route: str, app: Flask = None):
        """
        Add a route handler to the Flask app that handles incoming
        interaction data.

        If you are using Quart, you should use
        :meth:`.DiscordInteractions.set_route_async` instead.

        Parameters
        ----------
        route: str
            The URL path to receive interactions on.
        app: Flask
            The Flask app to add the route to.
        """

        if app is None:
            app = self.app

        @app.route(route, methods=["POST"])
        def interactions():
            result = self.handle_request()
            response, mimetype = result.encode()
            return Response(response, mimetype=mimetype)

    def set_route_async(self, route: str, app: Flask = None):
        """
        Add a route handler to a Quart app that handles incoming interaction
        data using asyncio.

        This function also sets up the aiohttp ClientSession that is used
        for sending followup messages, etc.

        Parameters
        ----------
        route: str
            The URL path to receive interactions on.
        app: Flask
            The Quart app to add the route to.
        """

        if app is None:
            app = self.app

        if aiohttp is None:
            raise ImportError(
                "The aiohttp module is required for async usage of this library"
            )

        @app.route(route, methods=["POST"])
        async def interactions():
            result = self.handle_request()

            if inspect.isawaitable(result):
                result = await result

            response, mimetype = result.encode()
            return Response(response, mimetype=mimetype)

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
