import dataclasses
from typing import Optional

from flask_discord_interactions.models.utils import LoadableDataclass


@dataclasses.dataclass
class Role(LoadableDataclass):
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
    icon
        Hash of the role's icon
    unicode_emoji
        Unicode emoji of the role (alternative to icons)
    """

    id: str
    name: str
    color: int
    hoist: bool
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: Optional[dict] = None
    icon: Optional[str] = None
    unicode_emoji: Optional[str] = None
