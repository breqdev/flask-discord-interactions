from dataclasses import dataclass
from typing import Callable, List, Optional, Union, TYPE_CHECKING
import inspect
import itertools
import types

import requests
from flask import Flask

from flask_discord_interactions.models import (
    LoadableDataclass,
    Member,
    Channel,
    Role,
    User,
    Attachment,
    CommandOptionType,
    ApplicationCommandType,
    Message,
    Component,
    Option,
)

if TYPE_CHECKING:
    from flask_discord_interactions.discord import DiscordInteractions


@dataclass
class Context(LoadableDataclass):
    """
    Represents the context in which a :class:`Command` or custom ID
    handler is invoked.

    Attributes
    ----------
    author
        A :class:`User` or  :class:`Member` object representing the invoking
        user.
    id
        The unique ID (snowflake) of this interaction.
    type
        The :class:`InteractionType` of this interaction.
    command_type
        The :class:`ApplicationCommandType` of this interaction.
    token
        The token to use when sending followup messages.
    channel_id
        The unique ID (snowflake) of the channel this command was invoked in.
    guild_id
        The unique ID (snowflake) of the guild this command was invoked in.
    options
        A list of the options passed to the command.
    values
        A list of the values selected, if this is a Select Menu handler.
    components
        The Modal's components with their submitted values, if this is a Modal handler.
    resolved
        Additional data ()
    command_name
        The name of the command that was invoked.
    command_id
        The unique ID (snowflake) of the command that was invoked.
    users
        :class:`User` objects for each user specified as an option.
    members
        :class:`Member` objects for each user specified as an option, if this
        command was invoked in a guild.
    channels
        :class:`Channel` objects for each channel specified as an option.
    roles
        :class:`Role` object for each role specified as an option.
    target
        The targeted :class:`User` or message.
    message
        The message that the invoked components are attached to.
        Only available on component interactions.
    locale
        The selected language of the invoking user.
    guild_locale
        The guild's preferred locale, if invoked in a guild.
    app_permissions
        Bitwise set of permissions the app or bot has within the channel the interaction was sent from.
    """

    author: Union[Member, User] = None
    id: str = None
    type: int = None
    command_type: int = None
    token: str = None
    channel_id: str = None
    guild_id: str = None
    options: list = None
    values: list = None
    components: list = None
    resolved: dict = None
    command_name: str = None
    command_id: str = None
    members: List[Member] = None
    channels: List[Channel] = None
    roles: List[Role] = None
    message: Message = None
    locale: Optional[str] = None
    guild_locale: Optional[str] = None
    app_permissions: Optional[str] = None
    app: Flask = None
    discord: "DiscordInteractions" = None

    custom_id: str = None
    primary_id: str = None
    handler_state: list = None

    target_id: str = None
    target: Union[User, Message] = None

    @classmethod
    def from_data(
        cls, discord: "DiscordInteractions" = None, app: Flask = None, data={}
    ):
        if data is None:
            data = {}

        # If this is a proxy (e.g. flask.current_app), get the current object
        # https://flask.palletsprojects.com/en/2.0.x/reqcontext/#notes-on-proxies
        if hasattr(app, "_get_current_object"):
            app = app._get_current_object()

        result = cls(
            app=app,
            discord=discord,
            id=data.get("id"),
            type=data.get("type"),
            command_type=data.get("data", {}).get("type")
            or ApplicationCommandType.CHAT_INPUT,
            token=data.get("token"),
            channel_id=data.get("channel_id"),
            guild_id=data.get("guild_id"),
            options=data.get("data", {}).get("options"),
            values=data.get("data", {}).get("values", []),
            components=data.get("data", {}).get("components", []),
            resolved=data.get("data", {}).get("resolved", {}),
            command_name=data.get("data", {}).get("name"),
            command_id=data.get("data", {}).get("id"),
            custom_id=data.get("data", {}).get("custom_id") or "",
            target_id=data.get("data", {}).get("target_id"),
            locale=data.get("locale"),
            guild_locale=data.get("guild_locale"),
            app_permissions=data.get("app_permissions"),
        )

        result.data = data

        result.parse_author(data)
        result.parse_message(data)
        result.parse_custom_id()
        result.parse_resolved()
        result.parse_target()
        result.parse_components()
        return result

    @property
    def auth_headers(self):
        if self.discord:
            return self.discord.auth_headers(self.app)
        else:
            return self.frozen_auth_headers

    def parse_author(self, data: dict):
        """
        Parse the author (invoking user) of this interaction.

        This will set :attr:`author` to a :class:`User` object if this
        interaction occurred in a direct message, or a :class:`Member` object
        if interaction occurred in a guild.

        Parameters
        ----------
        data
            The incoming interaction data.
        """
        if data.get("member"):
            self.author = Member.from_dict(data["member"])
        elif data.get("user"):
            self.author = User.from_dict(data["user"])
        else:
            self.author = None

    def parse_message(self, data: dict):
        """
        Parse the message out of in interaction.

        Parameters
        ----------
        data
            The incoming interaction data.
        """
        if data.get("message"):
            self.message = Message.from_dict(data["message"])
        else:
            self.message = None

    def parse_custom_id(self):
        """
        Parse the custom ID of the incoming interaction data.

        This includes the primary ID as well as any state stored in the
        handler.
        """

        self.primary_id = self.custom_id.split("\n", 1)[0]
        self.handler_state = self.custom_id.split("\n")

    def parse_resolved(self):
        """
        Parse the ``"resolved"`` section of the incoming interaction data.

        This section includes objects representing each user, member, channel,
        and role passed as an argument to the command.
        """

        self.members = {}
        for id in self.resolved.get("members", {}):
            member_info = self.resolved["members"][id]
            member_info["user"] = self.resolved["users"][id]
            self.members[id] = Member.from_dict(member_info)

        self.users = {
            id: User.from_dict(data)
            for id, data in self.resolved.get("users", {}).items()
        }

        self.channels = {
            id: Channel.from_dict(data)
            for id, data in self.resolved.get("channels", {}).items()
        }

        self.roles = {
            id: Role.from_dict(data)
            for id, data in self.resolved.get("roles", {}).items()
        }

        self.messages = {
            id: Message.from_dict(data)
            for id, data in self.resolved.get("messages", {}).items()
        }

        self.attachments = {
            id: Attachment.from_dict(data)
            for id, data in self.resolved.get("messages", {}).items()
        }

    def parse_target(self):
        """
        Parse the target of the incoming interaction.

        For User and Message commands, the target is the relevant user or
        message. This method sets the `ctx.target` field.
        """
        if self.command_type == ApplicationCommandType.USER:
            if self.target_id in self.members:
                self.target = self.members[self.target_id]
            else:
                self.target = self.users[self.target_id]
        elif self.command_type == ApplicationCommandType.MESSAGE:
            self.target = self.messages[self.target_id]
        else:
            self.target = None

    def parse_components(self):
        self.components = [Component.from_dict(c) for c in self.components]

    def create_args(self):
        """
        Create the arguments which will be passed to the function when the
        :class:`Command` is invoked.
        """
        if self.command_type == ApplicationCommandType.CHAT_INPUT:
            return self.create_args_chat_input()
        elif self.command_type == ApplicationCommandType.USER:
            return [self.target], {}
        elif self.command_type == ApplicationCommandType.MESSAGE:
            return [self.target], {}

    def create_args_chat_input(self):
        """
        Create the arguments for this command, assuming it is a ``CHAT_INPUT``
        command.
        """

        def create_args_recursive(data, resolved):
            if not data.get("options"):
                return [], {}

            args = []
            kwargs = {}

            for option in data["options"]:
                if option["type"] in [
                    CommandOptionType.SUB_COMMAND,
                    CommandOptionType.SUB_COMMAND_GROUP,
                ]:

                    args.append(option["name"])

                    sub_args, sub_kwargs = create_args_recursive(option, resolved)

                    args += sub_args
                    kwargs.update(sub_kwargs)

                elif option["type"] == CommandOptionType.USER:
                    if "members" in resolved:
                        member_data = resolved["members"][option["value"]]
                        member_data["user"] = resolved["users"][option["value"]]

                        kwargs[option["name"]] = Member.from_dict(member_data)
                    else:
                        kwargs[option["name"]] = User.from_dict(
                            resolved["users"][option["value"]]
                        )

                elif option["type"] == CommandOptionType.CHANNEL:
                    kwargs[option["name"]] = Channel.from_dict(
                        resolved["channels"][option["value"]]
                    )

                elif option["type"] == CommandOptionType.ROLE:
                    kwargs[option["name"]] = Role.from_dict(
                        resolved["roles"][option["value"]]
                    )

                elif option["type"] == CommandOptionType.ATTACHMENT:
                    kwargs[option["name"]] = Attachment.from_dict(
                        resolved["attachments"][option["value"]]
                    )

                else:
                    kwargs[option["name"]] = option["value"]

            return args, kwargs

        return create_args_recursive({"options": self.options}, self.resolved)

    def create_handler_args(self, handler: Callable):
        """
        Create the arguments which will be passed to the function when a
        custom ID handler is invoked.

        Parameters
        ----------
        handler: Callable
            The custom ID handler to create arguments for.
        """

        args = self.handler_state[1:]

        sig = inspect.signature(handler)

        iterator = zip(
            itertools.count(), args, itertools.islice(sig.parameters.values(), 1, None)
        )

        for i, argument, parameter in iterator:
            annotation = parameter.annotation

            if annotation == int:
                args[i] = int(argument)

            elif annotation == bool:
                if argument == "True":
                    args[i] = True
                elif argument == "False":
                    args[i] = False
                elif argument == "None":
                    args[i] = None
                else:
                    raise ValueError(
                        f"Invalid bool in handler state parsing: {args[i]}"
                    )

        return args

    def create_autocomplete_args(self):
        return [Option.from_data(option) for option in self.options]

    def followup_url(self, message: str = None):
        """
        Return the followup URL for this interaction. This URL can be used to
        send a new message, or to edit or delete an existing message.

        Parameters
        ----------
        message: str
            The ID of the message to edit or delete.
            If None, sends a new message.
            If "@original", refers to the original message.
        """

        url = (
            f"{self.app.config['DISCORD_BASE_URL']}/webhooks/"
            f"{self.app.config['DISCORD_CLIENT_ID']}/{self.token}"
        )
        if message is not None:
            url += f"/messages/{message}"

        return url

    def edit(self, updated: Union[Message, str], message: str = "@original"):
        """
        Edit an existing message.

        Parameters
        ----------
        updated: Union[Message, str]
            The updated Message to edit the message to.
        message: str
            The ID of the message to edit.
            If omitted, edits the original message.
        """

        updated = Message.from_return_value(updated)

        if not self.app or self.app.config["DONT_REGISTER_WITH_DISCORD"]:
            return

        response, mimetype = updated.encode(followup=True)
        updated = requests.patch(
            self.followup_url(message),
            data=response,
            headers={"Content-Type": mimetype},
        )
        updated.raise_for_status()

    def delete(self, message: str = "@original"):
        """
        Delete an existing message.

        Parameters
        ----------
        message: str
            The ID of the message to delete.
            If omitted, deletes the original message.
        """

        if not self.app or self.app.config["DONT_REGISTER_WITH_DISCORD"]:
            return

        response = requests.delete(self.followup_url(message))
        response.raise_for_status()

    def send(self, message: Union[Message, str]):
        """
        Send a new followup message.

        Parameters
        ----------
        message: Union[Message, str]
            The :class:`Message` to send as a followup message.
        """

        if not self.app or self.app.config["DONT_REGISTER_WITH_DISCORD"]:
            return

        message = Message.from_return_value(message)

        response, mimetype = message.encode(followup=True)
        message = requests.post(
            self.followup_url(), data=response, headers={"Content-Type": mimetype}
        )
        message.raise_for_status()
        return message.json()["id"]

    def get_command(self, command_name: str = None):
        """
        Get the ID of a command by name.

        Parameters
        ----------
        command_name: str
            The name of the command to get the ID of.
        """
        if command_name is None:
            return self.command_id
        else:
            try:
                return self.app.discord_commands[command_name].id
            except KeyError:
                raise ValueError(f"Unknown command: {command_name}")

    def freeze(self):
        "Return a copy of this Context that can be pickled for RQ and Celery."

        app = types.SimpleNamespace()

        CONFIG_KEYS = [
            "DISCORD_BASE_URL",
            "DISCORD_CLIENT_ID",
            "DONT_REGISTER_WITH_DISCORD",
        ]

        app.config = {key: self.app.config[key] for key in CONFIG_KEYS}

        new_context = Context.from_data(app=app, data=self.data)
        new_context.frozen_auth_headers = self.auth_headers

        return new_context

    def get_component(self, component_id: str):
        """
        Get a Component, only available for Modal Contexts.
        If the component was not found, raises a LookupError.

        Parameters
        ----------
        component_id: str
            The ID of the component to look up.
        """
        if not self.components:
            raise ValueError("This Context does not have any components.")
        for action_row in self.components:
            for component in action_row.components:
                if component.custom_id == component_id:
                    return component
        raise LookupError("The specified component was not found.")


@dataclass
class AsyncContext(Context):
    """
    Represents the context in which an asynchronous :class:`Command` is
    invoked. Also provides coroutine functions to handle followup messages.

    Users should not need to instantiate this class manually.
    """

    def __post_init__(self):
        if not self.app or self.app.config["DONT_REGISTER_WITH_DISCORD"]:
            return

        self.session = self.app.discord_client_session

    async def edit(self, updated: Union[str, Message], message: str = "@original"):
        """
        Edit an existing message.

        Parameters
        ----------
        updated: Union[str, Message]
            The updated Message to edit the message to.
        message: str
            The ID of the message to edit.
            If omitted, edits the original message.
        """

        updated = Message.from_return_value(updated)

        if not self.app or self.app.config["DONT_REGISTER_WITH_DISCORD"]:
            return

        response, mimetype = updated.encode(followup=True)
        await self.session.patch(
            self.followup_url(message),
            data=response,
            headers={"Content-Type": mimetype},
        )

    async def delete(self, message: str = "@original"):
        """
        Delete an existing message.

        Parameters
        ----------
        message: str
            The ID of the message to delete.
            If omitted, deletes the original message.
        """

        if not self.app or self.app.config["DONT_REGISTER_WITH_DISCORD"]:
            return

        await self.session.delete(self.followup_url(message))

    async def send(self, message: Union[Message, str]):
        """
        Send a new followup message.

        Parameters
        ----------
        message: Union[Message, str]
            The Message object to send as a followup message.
        """

        message = Message.from_return_value(message)

        if not self.app or self.app.config["DONT_REGISTER_WITH_DISCORD"]:
            return

        response, mimetype = message.encode(followup=True)
        async with self.session.post(
            self.followup_url(),
            data=response,
            headers={"Content-Type": mimetype},
        ) as message:
            return (await message.json())["id"]
