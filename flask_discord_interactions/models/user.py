import dataclasses
from typing import Optional, List

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
    public_flags
        Miscellaneous information about the user.
    avatar_hash
        The unique hash identifying the profile picture of the user.
    bot
        Whether the user is a bot account.
    system
        Whether the user is a Discord system account.
    """

    id: str
    username: str
    discriminator: str
    public_flags: int
    avatar_hash: Optional[str] = None
    bot: Optional[bool] = None
    system: Optional[bool] = None

    @classmethod
    def from_dict(cls, data):
        data = {**data, **data.get("user", {})}
        data["avatar_hash"] = data.get("avatar")
        return super().from_dict(data)

    @property
    def display_name(self):
        """
        The displayed name of the user (the username).

        Returns
        -------
        str
            The displayed name of the user.
        """
        return self.username

    @property
    def avatar_url(self):
        """
        The URL of the user's profile picture.

        Returns
        -------
        str
            The URL of the user's profile picture.
        """
        if self.avatar_hash is None:
            return f"https://cdn.discordapp.com/embed/avatars/{int(self.discriminator) % 5}.png"
        elif str(self.avatar_hash).startswith("a_"):
            return (
                f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar_hash}.gif"
            )
        else:
            return (
                f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar_hash}.png"
            )


@dataclasses.dataclass
class Member(User):
    """
    Represents a Member (a specific Discord :class:`User` in one particular
    guild.)

    Attributes
    ----------
    deaf
        Whether the user has been server deafened.
    mute
        Whether the user has been server muted.
    joined_at
        The timestamp that the user joined the guild at.
    avatar
        The member's guild avatar hash
    nick
        The guild nickname of the user.
    roles
        An array of role IDs that the user has.
    premium_since
        The timestamp that the user started Nitro boosting the guild at.
    permissions
        The permissions integer of the user.
    communication_disabled_until
        Timestamp when the member's timeout will expire (if existing)
    pending
        Whether the user has passed the membership requirements of a guild.
    """

    deaf: bool = False
    mute: bool = False
    joined_at: str = ""
    avatar: Optional[str] = None
    nick: Optional[str] = None
    roles: Optional[List[str]] = None
    premium_since: Optional[str] = None
    permissions: Optional[int] = None
    communication_disabled_until: Optional[str] = None
    pending: Optional[bool] = None

    def __post_init__(self):
        if isinstance(self.permissions, str):
            self.permissions = int(self.permissions)

    @property
    def display_name(self):
        """
        The displayed name of the user (their nickname, or if none exists,
        their username).

        Returns
        -------
        str
            The displayed name of the user.
        """
        return self.nick or self.username
