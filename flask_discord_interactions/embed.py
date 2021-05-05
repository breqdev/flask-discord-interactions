from dataclasses import dataclass
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
    url: str
    proxy_url: str
    height: int

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
