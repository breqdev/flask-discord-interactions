import dataclasses

from flask_discord_interactions.models.utils import LoadableDataclass


class ChannelType:
    "Represents the different :class:`Channel` type integers."
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6


@dataclasses.dataclass
class Channel(LoadableDataclass):
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
