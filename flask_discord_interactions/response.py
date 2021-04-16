import json


class ResponseType:
    "Represents the different response type integers."
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5


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
    def __init__(self, content=None, *, tts=False, embed=None, embeds=None,
                 allowed_mentions={"parse": ["roles", "users", "everyone"]},
                 deferred=False, ephemeral=False, file=None, files=None):
        self.content = content
        self.tts = tts

        if embed is not None and embeds is not None:
            raise ValueError("Specify only one of embed or embeds")
        if embed is not None:
            embeds = [embed]
        self.embeds = embeds

        if file is not None and files is not None:
            raise ValueError("Specify only one of file or files")
        if file is not None:
            files = [file]
        self.files = files

        self.allowed_mentions = allowed_mentions

        if deferred:
            self.response_type = \
                ResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
        else:
            self.response_type = \
                ResponseType.CHANNEL_MESSAGE_WITH_SOURCE

        self.flags = 64 if ephemeral else 0

        if (self.content is None and self.embeds is None
                and self.files is None and not deferred):
            raise ValueError(
                "Supply at least one of content, embeds, files, or deferred.")

        if ephemeral and (self.embeds is not None or self.files is not None):
            raise ValueError(
                "Ephemeral responses cannot include embeds or files.")

    @staticmethod
    def from_return_value(result):
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
            return Response()
        elif isinstance(result, Response):
            return result
        else:
            return Response(str(result))

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
