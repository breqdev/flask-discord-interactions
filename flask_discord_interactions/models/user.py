import dataclasses

from flask_discord_interactions.models.utils import LoadableDataclass


@dataclasses.dataclass
class User(LoadableDataclass):
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
        data["avatar_hash"] = data.get("avatar")
        return super().from_dict(data)

    @property
    def display_name(self):
        "The displayed name of the user (the username)."
        return self.username

    @property
    def avatar_url(self):
        "The URL of the user's profile picture."
        return "https://cdn.discordapp.com/avatars/" f"{self.id}/{self.avatar_hash}.png"


@dataclasses.dataclass
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
    permissions
        The permissions integer of the user.
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
    permissions: int = None
    deaf: bool = None
    mute: bool = None
    pending: bool = None

    def __post_init__(self):
        if isinstance(self.permissions, str):
            self.permissions = int(self.permissions)

    @property
    def display_name(self):
        """
        The displayed name of the user (their nickname, or if none exists,
        their username).
        """
        return self.nick or self.username
