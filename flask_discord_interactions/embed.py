from dataclasses import dataclass, asdict
from typing import List

@dataclass
class Footer:
    "Represents the footer of an Embed."
    text: str
    icon_url: str = None
    proxy_icon_url: str = None

@dataclass
class Field:
    "Represents a field on an Embed."
    name: str
    value: str
    inline: bool = False

@dataclass
class Media:
    "Represents a thumbnail, image, or video on an Embed."
    url: str = None
    proxy_url: str = None
    height: int = None
    width: int = None

@dataclass
class Provider:
    "Represents a provider of an Embed."
    name: str = None
    url: str = None

@dataclass
class Author:
    "Represents an author of an embed."
    name: str = None
    url: str = None
    icon_url: str = None
    proxy_icon_url: str = None

@dataclass
class Embed:
    """
    Represents an Embed to be sent as part of a Response.

    Attributes
    ----------
    title
        The title of the embed.
    description
        The description in the embed.
    url
        The URL that the embed title links to.
    timestamp
        An ISO8601 timestamp included in the embed.
    color
        An integer representing the color of the sidebar of the embed.
    footer
    image
    thumbnail
    video
    provider
    author
    fields
    """
    title: str = None
    description: str = None
    url: str = None
    timestamp: str = None
    color: int = None
    footer: Footer = None
    image: Media = None
    thumbnail: Media = None
    video: Media = None
    provider: Provider = None
    author: Author = None
    fields: List[Field] = None

    def dump(self):
        "Returns this Embed as a dictionary, removing fields which are None."
        def filter_none(d):
            if isinstance(d, dict):
                return {k: filter_none(v)
                        for k, v in d.items() if v is not None}
            else:
                return d

        return filter_none(asdict(self))
