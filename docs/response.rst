.. _response-page:

Response
========

Response objects are used whenever your bot responds to an Interaction or sends
or edits a followup message. They can contain content, embeds, files, and
other parameters depending on the situation.

In most cases, you can return a string and it will be converted into a
:class:`.Response` object:

.. code-block:: python

    @discord.command()
    def just_content(ctx):
        "Just normal string content"
        return "Just return a string to send it as a message"


    @discord.command()
    def markdown(ctx):
        "Fancy markdown tricks"
        return "All *the* **typical** ~~discord~~ _markdown_ `works` ***too.***"

Alternatively, you can create a Response object yourself:

.. code-block:: python

    @discord.command()
    def response_object(ctx):
        "Just normal string content"
        return Response("Return a Response object with the content")

You can also pass more options to the Response object, such as making the
response ephemeral:

.. code-block:: python

    @discord.command()
    def ephemeral(ctx):
        "Ephemeral Message"

        return Response(
            "Ephemeral messages are only sent to the user who ran the command, "
            "and they go away after a short while.\n\n"
            "Note that they cannot include embeds or files, "
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
            ctx.send(Response(
                content="Sending a file",
                file=("README.md", open("README.md", "r"), "text/markdown")))

        thread = threading.Thread(target=do_followup)
        thread.start()

        return "Sending an original message"

The ``allowed_mentions`` parameter can be used to restrict which users and
roles the message should mention. It is a good idea to use this whenever your
bot is echoing user input. You can read more about this parameter on the
`Discord API docs <https://discord.com/developers/docs/resources/channel#allowed-mentions-object>`_.

Full API
--------

.. autoclass:: flask_discord_interactions.Response
    :members:

|

.. autoclass:: flask_discord_interactions.ResponseType
    :members:
    :undoc-members:
    :member-order: bysource


