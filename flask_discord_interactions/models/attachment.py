import dataclasses
from typing import Optional

from flask_discord_interactions.models.utils import LoadableDataclass


@dataclasses.dataclass
class Attachment(LoadableDataclass):
    """
    Represents an attachment
    Attributes
    ----------
    id
        The id of the attachment
    filename
        Name of the attached file
    description
        Optional description of the file. Used for screen readers
    content_type
        The media type of the file
    size
        Size of the attached file in bytes
    url
        Url to fetch the file
    proxy_url
        Url to fetch the file from the discord media proxy
    height
        Optinal height if the file is an image
    width
        Optinal width if the file is an image
    ephemeral
        Set to true on ephemeral messages and when getting attachment as command option values
    """

    id: Optional[str] = None
    filename: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None
    url: Optional[str] = None
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None
    ephemeral: Optional[bool] = None
