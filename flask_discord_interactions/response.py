import json
import inspect
import dataclasses
from typing import List, Union


from flask_discord_interactions.embed import Embed
from flask_discord_interactions.component import Component


class ResponseType:
    "Represents the different response type integers."
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7


@dataclasses.dataclass
class Response:
    """
    Represents a response to a Discord interaction (incoming webhook)
    or a followup message (outgoing webhook).

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
        to only the user who used the slash command). Only valid for incoming
        webhooks.
    update
        Whether to update the initial message. Only valid for Message Component
        interactions / custom ID handlers.
    file
        The file to attach to the message. Only valid for outgoing webhooks.
    files
        An array of files to attach to the message. Speficy just one of
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
        default_factory=lambda: {"parse": ["roles", "users", "everyone"]})
    deferred: bool = False
    ephemeral: bool = False
    update: bool = False
    file: tuple = None
    files: List[tuple] = None
    components: List[Component] = None

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
            raise ValueError("Ephemeral responses cannot include files.")

        if self.embeds is not None:
            for i, embed in enumerate(self.embeds):
                if not dataclasses.is_dataclass(embed):
                    self.embeds[i] = Embed(**embed)

        if self.update:
            if self.deferred:
                self.response_type = ResponseType.DEFERRED_UPDATE_MESSAGE
            else:
                self.response_type = ResponseType.UPDATE_MESSAGE
        else:
            if self.deferred:
                self.response_type = \
                    ResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
            else:
                self.response_type = ResponseType.CHANNEL_MESSAGE_WITH_SOURCE

    @property
    def flags(self):
        """
        The flags sent with this response, determined by whether it is
        ephemeral.
        """
        return 64 if self.ephemeral else 0

    def dump_embeds(self):
        "Returns the embeds of this Response as a list of dicts."
        return [embed.dump() for embed in self.embeds] if self.embeds else None

    def dump_components(self):
        "Returns the message components as a list of dicts."
        return [c.dump() for c in self.components] if self.components else None

    @classmethod
    def from_return_value(cls, result):
        """
        Convert a function return value into a Response object.
        Converts ``None`` to an empty response, or any other type to ``str``
        as message content.

        Parameters
        ----------
        result
            The function return value to convert into a ``Response`` object.
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
        Return this ``Response`` as a dict to be sent in response to an
        incoming webhook.
        """

        if (self.content is None and self.embeds is None
                and self.files is None and not self.deferred):
            raise ValueError(
                "Supply at least one of content, embeds, files, or deferred.")

        if self.files:
            raise ValueError(
                "files are not allowed in an initial Interaction response")

        if self.update:
            raise ValueError("update is only valid for custom ID handlers")

        return {
            "type": self.response_type,
            "data": {
                "content": self.content,
                "tts": self.tts,
                "embeds": self.dump_embeds(),
                "allowed_mentions": self.allowed_mentions,
                "flags": self.flags,
                "components": self.dump_components()
            }
        }

    def dump_handler(self):
        """
        Return this ``Response`` as a dict to be sent in reply to a Message
        Component interaction.
        """

        if self.files:
            raise ValueError(
                "files are not allowed in a custom handler response")

        return {
            "type": self.response_type,
            "data": {
                "content": self.content,
                "tts": self.tts,
                "embeds": self.dump_embeds(),
                "allowed_mentions": self.allowed_mentions,
                "flags": self.flags,
                "components": self.dump_components()
            }
        }


    def dump_followup(self):
        """
        Return this ``Response`` as a dict to be sent to an outgoing webhook.
        """

        if (self.content is None and self.embeds is None
                and self.files is None and not self.deferred):
            raise ValueError(
                "Supply at least one of content, embeds, files, or deferred.")

        if self.ephemeral or self.deferred or self.update:
            raise ValueError(
                "ephemeral and deferred are not valid in followup responses")

        return {
            "content": self.content,
            "tts": self.tts,
            "embeds": self.dump_embeds(),
            "allowed_mentions": self.allowed_mentions,
            "components": self.dump_components()
        }

    def dump_multipart(self):
        """
        Return this ``Response`` to be sent to an outgoing webhook.
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
