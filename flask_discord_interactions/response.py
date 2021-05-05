import json
import dataclasses
from typing import List


class ResponseType:
    "Represents the different response type integers."
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5


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
        webhooks. You cannot use embeds with ephemeral messages.
    file
        The file to attach to the message. Only valid for outgoing webhooks.
    files
        An array of files to attach to the message. Speficy just one of
        ``file`` or ``files``. Only valid for outgoing webhooks.
    """
    content: str = None
    tts: bool = False
    embed: dict = None
    embeds: List[dict] = None
    allowed_mentions: dict = dataclasses.field(
        default_factory=lambda: {"parse": ["roles", "users", "everyone"]})
    deferred: bool = False
    ephemeral: bool = False
    file: tuple = None
    files: List[tuple] = None

    def __post_init__(self):
        if self.embed is not None and self.embeds is not None:
            raise ValueError("Specify only one of embed or embeds")
        if self.embed is not None:
            self.embeds = [self.embed]

        if self.file is not None and self.files is not None:
            raise ValueError("Specify only one of file or files")
        if self.file is not None:
            self.files = [self.file]

        if (self.content is None and self.embeds is None
                and self.files is None and not self.deferred):
            raise ValueError(
                "Supply at least one of content, embeds, files, or deferred.")

        if self.ephemeral and (
                self.embeds is not None or self.files is not None):
            raise ValueError(
                "Ephemeral responses cannot include embeds or files.")

    @property
    def response_type(self):
        "The Discord response type of the Interaction response."
        if self.deferred:
            return ResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
        else:
            return ResponseType.CHANNEL_MESSAGE_WITH_SOURCE

    @property
    def flags(self):
        """
        The flags sent with this response, determined by whether it is
        ephemeral.
        """
        return 64 if self.ephemeral else 0

    @property
    def allowed_initial(self):
        """
        Returns if this Response is valid to send as an initial Interaction
        response (i.e., if it does not contain files).
        """
        if self.files:
            return False
        return True

    @property
    def allowed_followup(self):
        """
        Returns if this Response is valid to send as a followup Interaction
        response/webhook (i.e., if it is not set as ephemeral or deferred).
        """
        if self.ephemeral:
            return False
        if self.deferred:
            return False
        return True

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

        if result is None:
            return cls()
        elif isinstance(result, cls):
            return result
        else:
            return cls(str(result))

    def dump(self):
        """
        Return this ``Response`` as a dict to be sent in response to an
        incoming webhook.
        """

        return {
            "type": self.response_type,
            "data": {
                "content": self.content,
                "tts": self.tts,
                "embeds": self.embeds,
                "allowed_mentions": self.allowed_mentions,
                "flags": self.flags
            }
        }

    def dump_followup(self):
        """
        Return this ``Response`` as a dict to be sent to an outgoing webhook.
        """

        return {
            "content": self.content,
            "tts": self.tts,
            "embeds": self.embeds,
            "allowed_mentions": self.allowed_mentions
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
