import dataclasses
from typing import Optional

from flask_discord_interactions.models.utils import LoadableDataclass


class ChannelType:
    "Represents the different :class:`Channel` type integers."
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6  # deprecated
    ANNOUNCEMENT_THREAD = 10
    PUBLIC_THREAD = 11
    PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13
    GUILD_DIRECTORY = 14
    GUILD_FORUM = 15


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
    nsfw
        Whether the channel is age restricted or not.
    parent_id
        Category this channel belongs to.
    thread_metadata
        Thread-specific fields not needed by other channels.
    """

    id: str
    name: str
    permissions: int
    type: int
    nsfw: Optional[bool] = False
    parent_id: Optional[bool] = None
    thread_metadata: Optional[dict] = None
