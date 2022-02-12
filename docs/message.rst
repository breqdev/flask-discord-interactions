.. _response-page:

Message Models
==============

Message object
--------------

Message objects are used whenever your bot responds to an Interaction or sends
or edits a followup message. They can contain content, embeds, files, and
other parameters depending on the situation.

In most cases, you can return a string and it will be converted into a
:class:`.Message` object:

.. code-block:: python

    @discord.command()
    def just_content(ctx):
        "Just normal string content"
        return "Just return a string to send it as a message"


    @discord.command()
    def markdown(ctx):
        "Fancy markdown tricks"
        return "All *the* **typical** ~~discord~~ _markdown_ `works` ***too.***"

Alternatively, you can create a Message object yourself:

.. code-block:: python

    from flask_discord_interactions import Message

    @discord.command()
    def message_object(ctx):
        "Just normal string content"
        return Message("Return a Message object with the content")

You can also pass more options to the Message object, such as making the
response ephemeral:

.. code-block:: python

    @discord.command()
    def ephemeral(ctx):
        "Ephemeral Message"

        return Message(
            "Ephemeral messages are only sent to the user who ran the command, "
            "and they go away after a short while.\n\n"
            "Note that they cannot include files, "
            "but Markdown is *perfectly fine.*",
            ephemeral=True
        )

Note that this only works with the initial response, not for followup messages.

For followup messages (*not* the initial response), you can also attach files:

.. code-block:: python

    @discord.command()
    def followup(ctx):
        def do_followup():
            print("Followup task started")
            time.sleep(5)

            print("Sending a file")
            ctx.send(Message(
                content="Sending a file",
                file=("README.md", open("README.md", "rb"), "text/markdown")))

        thread = threading.Thread(target=do_followup)
        thread.start()

        return "Sending an original message"

Pass files as a tuple, containing:
- The filename
- A file object (typically the result of a call to ``open(filename, "rb")`` , but you could use something like :class:`io.BytesIO` too)
- Optionally, the content-type of the file

See the ``files`` parameter of :func:`requests.request` for details.

The ``allowed_mentions`` parameter can be used to restrict which users and
roles the message should mention. It is a good idea to use this whenever your
bot is echoing user input. You can read more about this parameter on the
`Discord API docs <https://discord.com/developers/docs/resources/channel#allowed-mentions-object>`_.

Full API
^^^^^^^^

.. autoclass:: flask_discord_interactions.Message(**kwargs)
    :members:

|

.. autoclass:: flask_discord_interactions.ResponseType
    :members:
    :undoc-members:
    :member-order: bysource

Embeds
------

Embed objects let you represent Embeds which you can return as part of
messages.

.. code-block:: python

    from flask_discord_interactions import Embed, embed

    @discord.command()
    def my_embed(ctx):
        "Embeds!"

        return Message(embed=Embed(
            title="Embeds!",
            description="Embeds can be specified as Embed objects.",
            fields=[
                embed.Field(
                    name="Can they use markdown?",
                    value="**Yes!** [link](https://google.com/)"
                ),
                embed.Field(
                    name="Where do I learn about how to format this object?",
                    value=("[Try this visualizer!]"
                        "(https://leovoel.github.io/embed-visualizer/)")
                )
            ]
        ))

The :class:`.Embed` class represents a single Embed. You can also use
:class:`.embed.Field`, :class:`.embed.Author`, :class:`.embed.Footer`, or
:class:`.embed.Provider` for those fields. :class:`.embed.Media` can be used
for images, videos, and thumbnails.

Full API
^^^^^^^^

.. autoclass:: flask_discord_interactions.Embed(**kwargs)
    :members:

|

.. autoclass:: flask_discord_interactions.embed.Field
    :members:
    :undoc-members:

|

.. autoclass:: flask_discord_interactions.embed.Author
    :members:
    :undoc-members:

|

.. autoclass:: flask_discord_interactions.embed.Footer
    :members:
    :undoc-members:

|

.. autoclass:: flask_discord_interactions.embed.Provider
    :members:
    :undoc-members:

|

.. autoclass:: flask_discord_interactions.embed.Media
    :members:
    :undoc-members:
