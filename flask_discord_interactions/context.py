from dataclasses import dataclass
from typing import List
import inspect

import requests

try:
    import aiohttp
except ImportError:
    aiohttp = None

from flask_discord_interactions.response import Response


class CommandOptionType:
    "Represents the different option type integers."
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


class ChannelType:
    "Represents the different :class:`Channel` type integers."
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6


class ContextObject:
    @classmethod
    def from_dict(cls, data):
        """
        Construct the Context object from a dictionary, skipping any keys
        in the dictionary that do not correspond to fields of the class.

        Parameters
        ----------
        data
            A dictionary of fields to set on the Context object.
        """
        return cls(**{
            k: v for k, v in data.items()
            if k in inspect.signature(cls).parameters
        })


@dataclass
class User(ContextObject):
    """
    Represents a User (the identity of a Discord user, not tied to any
    specific guild).

    Attributes
    ----------
    id
        The ID (snowflake) of the user.
    username
        The Discord username of the user.
    discriminator
        The code following the # after the username.
    avatar_hash
        The unique hash identifying the profile picture of the user.
    bot
        Whether the user is a bot account.
    system
        Whether the user is a Discord system account.
    mfa_enabled
        Whether the user has enabled Two-Factor Authentication.
    locale
        The locale of the user.
    flags
        Miscellaneous information about the user.
    premium_type
        The Nitro status of the user.
    public_flags
        Miscellaneous information about the user.
    """
    id: str = None
    username: str = None
    discriminator: str = None
    avatar_hash: str = None
    bot: bool = None
    system: bool = None
    mfa_enabled: bool = None
    locale: str = None
    flags: int = None
    premium_type: int = None
    public_flags: int = None

    @classmethod
    def from_dict(cls, data):
        data = {**data, **data.get("user", {})}
        return super().from_dict(data)

    @property
    def display_name(self):
        "The displayed name of the user (the username)."
        return self.username

    @property
    def avatar_url(self):
        "The URL of the user's profile picture."
        return ("https://cdn.discordapp.com/avatars/"
                f"{self.id}/{self.avatar_hash}.png")


@dataclass
class Member(User):
    """
    Represents a Member (a specific Discord :class:`User` in one particular
    guild.)

    Attributes
    ----------
    nick
        The guild nickname of the user.
    roles
        An array of role IDs that the user has.
    joined_at
        The timestamp that the user joined the guild at.
    premium_since
        The timestamp that the user started Nitro boosting the guild at.
    deaf
        Whether the user has been server deafened.
    mute
        Whether the user has been server muted.
    pending
        Whether the user has passed the membership requirements of a guild.
    """
    nick: str = None
    roles: list = None
    joined_at: str = None
    premium_since: str = None
    deaf: bool = None
    mute: bool = None
    pending: bool = None

    @property
    def display_name(self):
        """
        The displayed name of the user (their nickname, or if none exists,
        their username).
        """
        return self.nick or self.username


@dataclass
class Channel(ContextObject):
    """
    Represents a Channel in Discord. This includes voice channels, text
    channels, and channel categories.

    Attributes
    ----------
    id
        The unique ID (snowflake) of the channel.
    name
        The name of the channel.
    permissions
        The permissions integer of the invoking user in that channel.
    type
        The type of channel.
    """
    id: str = None
    name: str = None
    permissions: int = None
    type: int = None


@dataclass
class Role(ContextObject):
    """
    Represents a Role in Discord.

    Attributes
    ----------
    id
        The unique ID (snowflake) of the role.
    name
        The name of the role.
    color
        The color given to the role.
    hoist
        Whether the role is displayed separately in the member list.
    position
        The position of the role in the roles list.
    permissions
        The permissions integer of the role.
    managed
        Whether the role is managed by an integration (bot).
    mentionable
        Whether the role can be mentioned by all users.
    tags
        Miscellaneous information about the role.
    """
    id: str = None
    name: str = None
    color: str = None
    hoist: bool = None
    position: int = None
    managed: bool = None
    mentionable: bool = None
    tags: dict = None


@dataclass
class Context(ContextObject):
    """
    Represents the context in which a :class:`SlashCommand` is invoked.

    Attributes
    ----------
    author
        A :class:`Member` object representing the invoking user.
    id
        The unique ID (snowflake) of this interaction.
    token
        The token to use when sending followup messages.
    channel_id
        The unique ID (snowflake) of the channel this command was invoked in.
    guild_id
        The unique ID (snowflake) of the guild this command was invoked in.
    options
        An array of the options passed to the command.
    command_name
        The name of the command that was invoked.
    command_id
        The unique ID (snowflake) of the command that was invoked.
    members
        :class:`Member` objects for each user specified as an option.
    channels
        :class:`Channel` objects for each channel specified as an option.
    roles
        :class:`Role` object for each role specified as an option.
    """
    author: Member = None
    id: str = None
    token: str = None
    channel_id: str = None
    guild_id: str = None
    options: list = None
    command_name: str = None
    command_id: str = None
    members: List[Member] = None
    channels: List[Channel] = None
    roles: List[Role] = None

    client_id: str = ""
    auth_headers: dict = None

    @classmethod
    def from_data(cls, discord=None, app=None, data={}):
        if data is None:
            data = {}

        result = cls(
            client_id = app.config["DISCORD_CLIENT_ID"] if app else "",
            auth_headers = discord.auth_headers(app) if discord else {},
            author = Member.from_dict(data.get("member", {})),
            id = data.get("id"),
            token = data.get("token"),
            channel_id = data.get("channel_id"),
            guild_id = data.get("guild_id"),
            options = data.get("data", {}).get("options"),
            command_name = data.get("data", {}).get("name"),
            command_id = data.get("data", {}).get("id")
        )

        result.parse_resolved(data.get("data", {}).get("resolved", {}))
        return result

    def parse_resolved(self, data):
        """
        Parse the ``"resolved"`` section of the incoming interaction data.

        This section includes objects representing each user, member, channel,
        and role passed as an argument to the command.

        Parameters
        ----------
        data
            The ``"resolved"`` section of the incoming interaction data.
        """

        self.members = {}
        for id in data.get("members", {}):
            member_info = data["members"][id]
            member_info["user"] = data["users"][id]
            self.members[id] = Member.from_dict(member_info)

        self.channels = {id: Channel.from_dict(data)
                         for id, data in data.get("channels", {}).items()}

        self.roles = {id: Role.from_dict(data)
                      for id, data in data.get("roles", {}).items()}

    def create_args(self, data, resolved):
        """
        Create the arguments which will be passed to the function when the
        :class:`SlashCommand` is invoked.

        This function is recursive: when a subcommand is invoked, this function
        will call itself with the subcommand option data. This is why the
        ``"resolved"`` data is passed as a separate argument.

        Parameters
        ----------
        data
            An object with the incoming data for the invocation.
        resolved
            The ``"resolved"`` section of the incoming interaction data.
        """

        if "options" not in data:
            return [], {}

        args = []
        kwargs = {}
        for option in data["options"]:
            if option["type"] in [
                    CommandOptionType.SUB_COMMAND,
                    CommandOptionType.SUB_COMMAND_GROUP]:
                args.append(option["name"])
                sub_args, sub_kwargs = self.create_args(option, resolved)
                args += sub_args
                kwargs.update(sub_kwargs)
            elif option["type"] == CommandOptionType.USER:
                member_data = resolved["members"][option["value"]]
                member_data["user"] = resolved["users"][option["value"]]

                kwargs[option["name"]] = Member.from_dict(member_data)
            elif option["type"] == CommandOptionType.CHANNEL:
                kwargs[option["name"]] = Channel.from_dict(
                    resolved["channels"][option["value"]])
            elif option["type"] == CommandOptionType.ROLE:
                kwargs[option["name"]] = Role.from_dict(
                    resolved["roles"][option["value"]])
            else:
                kwargs[option["name"]] = option["value"]

        return args, kwargs

    def followup_url(self, message=None):
        """
        Return the followup URL for this interaction. This URL can be used to
        send a new message, or to edit or delete an existing message.

        Parameters
        ----------
        message
            The message to edit or delete. If None, sends a new message. If
            "@original", refers to the original message.
        """

        url = ("https://discord.com/api/v8/webhooks/"
               f"{self.client_id}/{self.token}")
        if message is not None:
            url += f"/messages/{message}"

        return url

    def edit(self, response, message="@original"):
        """
        Edit an existing message.

        Parameters
        ----------
        response
            The new response to edit the message to.
        message
            The message to edit. If omitted, edits the original message.
        """

        response = Response.from_return_value(response)

        response = requests.patch(
            self.followup_url(message),
            json=response.dump_followup(),
            headers=self.auth_headers
        )
        response.raise_for_status()

    def delete(self, message="@original"):
        """
        Delete an existing message.

        Parameters
        ----------
        message
            The message to delete. If omitted, deletes the original message.
        """

        response = requests.delete(
            self.followup_url(message),
            headers=self.auth_headers
        )
        response.raise_for_status()

    def send(self, response):
        """
        Send a new followup message.

        Parameters
        ----------
        response
            The response to send as a followup message.
        """

        response = Response.from_return_value(response)

        response = requests.post(
            self.followup_url(),
            headers=self.auth_headers,
            **response.dump_multipart()
        )
        response.raise_for_status()
        return response.json()["id"]


@dataclass
class AsyncContext(Context):
    """
    Represents the context in which an asynchronous :class:`SlashCommand` is
    invoked. Also provides coroutine functions to handle followup messages.

    Users should not need to instantiate this class manually.
    """

    def __post_init__(self):
        self.session = aiohttp.ClientSession(
            headers=self.auth_headers,
            raise_for_status=True,
        )

        if aiohttp is None:
            raise ValueError("aiohttp is required to create async contexts")

    async def edit(self, response, message="@original"):
        """
        Edit an existing message.

        Parameters
        ----------
        response
            The new response to edit the message to.
        message
            The message to edit. If omitted, edits the original message.
        """

        response = Response.from_return_value(response)

        await self.session.patch(
            self.followup_url(message), json=response.dump_followup()
        )

    async def delete(self, message="@original"):
        """
        Delete an existing message.

        Parameters
        ----------
        message
            The message to delete. If omitted, deletes the original message.
        """

        await self.session.delete(self.followup_url(message))

    async def send(self, response):
        """
        Send a new followup message.

        Parameters
        ----------
        response
            The response to send as a followup message.
        """

        response = Response.from_return_value(response)

        async with self.session.post(
            self.followup_url(),
            headers=self.auth_headers,
            **response.dump_multipart()
        ) as response:
            return (await response.json())["id"]

    async def close(self):
        await self.session.close()