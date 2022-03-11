import dataclasses
from flask_discord_interactions.models.user import Member
import inspect
from typing import List, Union
import json
from datetime import datetime

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
                self.Message_type = ResponseType.DEFERRED_UPDATE_MESSAGE
            else:
                self.Message_type = ResponseType.UPDATE_MESSAGE
        else:
            if self.deferred:
                self.Message_type = ResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
            else:
                self.Message_type = ResponseType.CHANNEL_MESSAGE_WITH_SOURCE

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
        """
        return 64 if self.ephemeral else 0

    def dump_embeds(self):
        "Returns the embeds of this Message as a list of dicts."
        return (
            [embed.dump() for embed in self.embeds] if self.embeds is not None else None
        )

    def dump_components(self):
        "Returns the message components as a list of dicts."
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

    def dump(self):
        """
        Return this ``Message`` as a dict to be sent in Message to an
        incoming webhook.
        """

        if (
            self.content is None
            and self.embeds is None
            and self.files is None
            and not self.deferred
        ):
            raise ValueError(
                "Supply at least one of content, embeds, files, or deferred."
            )

        if self.files:
            raise ValueError("files are not allowed in an initial Interaction Message")

        if self.update:
            raise ValueError("update is only valid for custom ID handlers")

        return {
            "type": self.Message_type,
            "data": {
                "content": self.content,
                "tts": self.tts,
                "embeds": self.dump_embeds(),
                "allowed_mentions": self.allowed_mentions,
                "flags": self.flags,
                "components": self.dump_components(),
            },
        }

    def dump_handler(self):
        """
        Return this ``Message`` as a dict to be sent in reply to a Message
        Component interaction.
        """

        if self.files:
            raise ValueError("files are not allowed in a custom handler Message")

        return {
            "type": self.Message_type,
            "data": {
                "content": self.content,
                "tts": self.tts,
                "embeds": self.dump_embeds(),
                "allowed_mentions": self.allowed_mentions,
                "flags": self.flags,
                "components": self.dump_components(),
            },
        }

    def dump_followup(self):
        """
        Return this ``Message`` as a dict to be sent to an outgoing webhook.
        """

        if (
            self.content is None
            and self.embeds is None
            and self.files is None
            and not self.deferred
        ):
            raise ValueError(
                "Supply at least one of content, embeds, files, or deferred."
            )

        if self.ephemeral or self.deferred or self.update:
            raise ValueError(
                "ephemeral and deferred are not valid in followup Messages"
            )

        return {
            "content": self.content,
            "tts": self.tts,
            "embeds": self.dump_embeds(),
            "allowed_mentions": self.allowed_mentions,
            "components": self.dump_components(),
        }

    def dump_multipart(self):
        """
        Return this ``Message`` to be sent to an outgoing webhook.
        Handles multipart encoding for file attachments.

        Returns an object that may have ``data``, ``files``, or ``json``
        fields.
        """

        if self.files:
            payload_json = json.dumps(self.dump_followup())

            multipart = []
            for file in self.files:
                multipart.append(("file", file))

            return {"data": {"payload_json": payload_json}, "files": multipart}
        else:
            return {"json": self.dump_followup()}
