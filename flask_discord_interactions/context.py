import requests

from .response import Response


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


class User:
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

    def __init__(self, data=None):
        if data:
            self.id = data.get("id")
            self.username = data.get("username")
            self.discriminator = data.get("discriminator")
            self.avatar_hash = data.get("avatar")
            self.bot = data.get("bot", False)
            self.system = data.get("system", False)
            self.mfa_enabled = data.get("mfa_enabled", False)
            self.locale = data.get("locale")
            self.flags = data.get("flags")
            self.premium_type = data.get("premium_type")
            self.public_flags = data.get("public_flags")

    @property
    def display_name(self):
        "The displayed name of the user (the username)."
        return self.username

    @property
    def avatar_url(self):
        "The URL of the user's profile picture."
        return ("https://cdn.discordapp.com/avatars/"
                f"{self.id}/{self.avatar_hash}.png")


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

    def __init__(self, data=None):
        if data:
            super().__init__(data["user"])

            self.nick = data.get("nick")
            self.roles = data.get("roles")
            self.joined_at = data.get("joined_at")
            self.premium_since = data.get("premium_since")
            self.deaf = data.get("deaf")
            self.mute = data.get("mute")
            self.pending = data.get("pending")

    @property
    def display_name(self):
        """
        The displayed name of the user (their nickname, or if none exists,
        their username).
        """
        return self.nick or self.username


class Channel:
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

    def __init__(self, data=None):
        if data:
            self.id = data.get("id")
            self.name = data.get("name")
            self.permissions = data.get("permissions")
            self.type = data.get("type")


class Role:
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

    def __init__(self, data=None):
        if data:
            self.id = data.get("id")
            self.name = data.get("name")
            self.color = data.get("color")
            self.hoist = data.get("hoist")
            self.position = data.get("position")
            self.permissions = data.get("permissions")
            self.managed = data.get("managed")
            self.mentionable = data.get("mentionable")
            self.tags = data.get("tags", {})


class Context:
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

    def __init__(self, discord, app, data=None):
        self.client_id = app.config["DISCORD_CLIENT_ID"]
        self.auth_headers = discord.auth_headers(app)

        if data:
            self.author = Member(data["member"])
            self.id = data["id"]
            self.token = data["token"]
            self.channel_id = data["channel_id"]
            self.guild_id = data["guild_id"]
            self.options = data["data"].get("options")
            self.command_name = data["data"]["name"]
            self.command_id = data["data"]["id"]

            self.parse_resolved(data["data"].get("resolved", {}))

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
            self.members[id] = Member(member_info)

        self.channels = {id: Channel(data)
                         for id, data in data.get("channels", {}).items()}

        self.roles = {id: Role(data)
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

                kwargs[option["name"]] = Member(member_data)
            elif option["type"] == CommandOptionType.CHANNEL:
                kwargs[option["name"]] = Channel(
                    resolved["channels"][option["value"]])
            elif option["type"] == CommandOptionType.ROLE:
                kwargs[option["name"]] = Role(
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
