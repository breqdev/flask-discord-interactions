import dataclasses
from flask_discord_interactions.models.user import Member
import inspect
from typing import List, Union
import json
from datetime import datetime
import requests_toolbelt

from flask_discord_interactions.models.utils import LoadableDataclass
from flask_discord_interactions.models.component import Component
from flask_discord_interactions.models.embed import Embed

from flask_discord_interactions.enums import ResponseType


@dataclasses.dataclass
class Message(LoadableDataclass):
    """
    Represents a Message, often a response to a Discord interaction (incoming
    webhook) or a followup message (outgoing webhook).

    Attributes
    ----------

    content
        The message body/content.
    tts
        Whether the message should be sent with text-to-speech.
    embed
        The embed object (dict) accompanying the message.
    embeds
        An array of embed objects. Specify just one of ``embed`` or ``embeds``.
    allowed_mentions
        An object representing which roles and users the message is allowed
        to mention. See the Discord API docs for details.
    deferred
        Whether the message should be deferred (display a loading state
        to the user temporarily). Only valid for incoming webhooks.
    ephemeral
        Whether the message should be ephemeral (only displayed temporarily
        to only the user who used the command). Only valid for incoming
        webhooks.
    update
        Whether to update the initial message. Only valid for Message Component
        interactions / custom ID handlers.
    file
        The file to attach to the message. Only valid for outgoing webhooks.
        Pass a 2-tuple containing the file name and a file object, e.g.

        .. code-block:: python

            ("README.md", open("README.md", "rb"))

        See the ``files`` parameter of :func:`requests.request` for details.
    files
        A list of files to attach to the message. Specify just one of
        ``file`` or ``files``. Only valid for outgoing webhooks.
    components
        An array of :class:`.Component` objects representing message
        components.
    """

    content: str = None
    tts: bool = False
    embed: Union[Embed, dict] = None
    embeds: List[Union[Embed, dict]] = None
    allowed_mentions: dict = dataclasses.field(
        default_factory=lambda: {"parse": ["roles", "users", "everyone"]}
    )
    deferred: bool = False
    ephemeral: bool = False
    update: bool = False
    file: tuple = None
    files: List[tuple] = None
    components: List[Component] = None

    # These fields are only set on incoming messages
    id: str = None
    channel_id: str = None
    timestamp: datetime = None
    edited_timestamp: datetime = None
    author: Member = None

    def __post_init__(self):
        if self.embed is not None and self.embeds is not None:
            raise ValueError("Specify only one of embed or embeds")
        if self.embed is not None:
            self.embeds = [self.embed]

        if self.file is not None and self.files is not None:
            raise ValueError("Specify only one of file or files")
        if self.file is not None:
            self.files = [self.file]

        if self.ephemeral and self.files is not None:
            raise ValueError("Ephemeral Messages cannot include files.")

        if self.embeds is not None:
            for i, embed in enumerate(self.embeds):
                if not dataclasses.is_dataclass(embed):
                    self.embeds[i] = Embed.from_dict(embed)

        if self.update:
            if self.deferred:
                self.response_type = ResponseType.DEFERRED_UPDATE_MESSAGE
            else:
                self.response_type = ResponseType.UPDATE_MESSAGE
        else:
            if self.deferred:
                self.response_type = ResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
            else:
                self.response_type = ResponseType.CHANNEL_MESSAGE_WITH_SOURCE

        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

        if isinstance(self.edited_timestamp, str):
            self.edited_timestamp = datetime.fromisoformat(self.edited_timestamp)

        if isinstance(self.author, dict):
            self.author = Member.from_dict(self.author)

    @property
    def flags(self):
        """
        The flags sent with this Message, determined by whether it is
        ephemeral.

        Returns
        -------
        int
            Integer representation of the flags.
        """
        return 64 if self.ephemeral else 0

    def dump_embeds(self):
        """
        Returns the embeds of this Message as a list of dicts.

        Returns
        -------
        List[dict]
            A list of dicts representing the embeds.
        """
        return (
            [embed.dump() for embed in self.embeds] if self.embeds is not None else None
        )

    def dump_components(self):
        """
        Returns the message components as a list of dicts.

        Returns
        -------
        List[dict]
            A list of dicts representing the components.
        """
        return (
            [c.dump() for c in self.components] if self.components is not None else None
        )

    @classmethod
    def from_return_value(cls, result):
        """
        Convert a function return value into a Message object.
        Converts ``None`` to an empty Message, or any other type to ``str``
        as message content.

        Parameters
        ----------
        result
            The function return value to convert into a ``Message`` object.

        Returns
        -------
        Message
            A ``Message`` object representing the return value.
        """

        async def construct_async(result):
            return cls.from_return_value(await result)

        if result is None:
            return cls()
        elif inspect.isawaitable(result):
            return construct_async(result)
        elif isinstance(result, cls):
            return result
        else:
            return cls(str(result))

    def encode(self, followup=False):
        """
        Return this ``Message`` as a string/mimetype pair for sending to Discord.

        If the message contains no files, the string will be a serialized
        JSON object and the mimetype will be ``application/json``.

        If the message contains attachments, the string will be a multipart
        encoded response and the mimetype will be ``multipart/form-data``.

        Parameters
        ----------
        followup: bool
            Whether this is a followup message.

        Returns
        -------
        string
            A string containing the message data (either JSON or multipart).
        string
            The mimetype of the message data.
        """

        payload = {
            "content": self.content,
            "tts": self.tts,
            "embeds": self.dump_embeds(),
            "allowed_mentions": self.allowed_mentions,
            "flags": self.flags,
            "components": self.dump_components(),
        }

        if not followup:
            payload = {
                "type": self.response_type,
                "data": payload,
            }

        payload_json = json.dumps(payload)

        if self.files:
            fields = [
                ("payload_json", (None, payload_json.encode(), "application/json"))
            ]

            for i, file in enumerate(self.files):
                fields.append((f"files[{i}]", file))

            multipart = requests_toolbelt.MultipartEncoder(
                fields=fields,
            )

            return (multipart.to_string().decode(), multipart.content_type)
        else:
            return (payload_json, "application/json")
