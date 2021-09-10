Client
======

The :class:`.Client` class can simulate calling a :class:`.Command`
without connecting to Discord. This is useful for unit testing.

The :class:`.Client` must be initialized by passing a
:class:`.DiscordInteractions` object:

.. code-block:: python

    from flask import Flask
    from flask_discord_interactions import DiscordInteractions, Client


    app = Flask(__name__)
    discord = DiscordInteractions(app)

    test_client = Client(discord)

From here, the :class:`.Client` can be used to simulate calling commands.
Parameters can be passed in as keyword arguments.

.. code-block:: python

    @discord.command()
    def ping(ctx, pong: str = "pong"):
        "Respond with a friendly 'pong'!"
        return f"Pong {pong}!"


    print(test_client.run("ping"))
    print(test_client.run("ping", pong="ping"))


Groups can be called by specifying additional positional arguments.

.. code-block:: python

    groupy = discord.command_group("groupy")

    @groupy.command()
    def group(ctx, embed: bool):
        if embed:
            return Message(embed={"title": "Groupy group"})
        else:
            return "Groupy group"


    print(test_client.run("groupy", "group", True))
    print(test_client.run("groupy", "group", False))

It's possible to pass in a :class:`.Member`, :class:`.Channel`, or
:class:`.Role` object as a parameter as well.

.. code-block:: python

    @discord.command()
    def channel_name(ctx, channel: Channel):
        return channel.name

    client.run("channel_name", channel=Channel(name="general"))

Finally, you can use the :meth:`.Client.context` context manager to specify
the context of the interaction.

.. code-block:: python

    @discord.command()
    def uses_context(ctx):
        return f"Your name is {ctx.author.display_name}"

    context = Context(author=Member(username="Bob"))

    with test_client.context(context):
        print(test_client.run("uses_context"))

Full API
--------

.. autoclass:: flask_discord_interactions.Client
    :members: