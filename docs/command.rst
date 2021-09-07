.. _command-page:

Command
=======

In Flask-Discord-Interactions, commands are created with a declarative syntax
that should be familiar to users of Discord.py.

Slash Commands
--------------

Commands are created using the :meth:`.DiscordInteractions.command`
decorator.

Here is a basic command:

.. code-block:: python

    @discord.command()
    def ping(ctx):
        "Respond with a friendly 'pong'!"
        return "Pong!"

The ``ctx`` parameter is a :class:`.Context` object.
For more information about it, see :ref:`context-page`.

Options can be provided as parameters to this command. See
:ref:`options-page` for details.

The function must return either a string or a
:class:`.Response` object. For
more information about what kind of responses are valid, see
:ref:`response-page`.

User Commands
-------------

User Commands are created using the :meth:`.DiscordInteractions.command`
decorator. The ``type`` needs to be specified using the
:class:`.ApplicationCommandType.USER`.

Here is a basic command:

.. code-block:: python

    @discord.command(type=ApplicationCommandType.USER)
    def userCmd(ctx):
        return "something"

Options and Description cannot be provided.

Message Commands
-------------

User Commands are created using the :meth:`.DiscordInteractions.command`
decorator. The ``type`` needs to be specified using the
:class:`.ApplicationCommandType.MESSAGE`.

Here is a basic command:

.. code-block:: python

    @discord.command(type=ApplicationCommandType.MESSAGE)
    def msgCmd(ctx):
        return "something"

Options and Description cannot be provided.

Advanced Usage
^^^^^^^^^^^^^^

If you use the ``options`` parameter of the
:meth:`.DiscordInteractions.command` decorator to specify options manually,
then it will override the options inferred from the function arguments
and type annotation. You can use this to, for instance, route multiple
subcommands with different options to the same function. This isn't the
recommended approach, but it is supported by the API.

.. code-block:: python

    @discord.command(options=[
        {
            "name": "google",
            "description": "Search with Google",
            "type": CommandOptionType.SUB_COMMAND,
            "options": [{
                "name": "query",
                "description": "Search query",
                "type": CommandOptionType.STRING,
                "required": True
            }]
        },
        {
            "name": "bing",
            "description": "Search with Bing",
            "type": CommandOptionType.SUB_COMMAND,
            "options": [{
                "name": "query",
                "description": "Search query",
                "type": CommandOptionType.STRING,
                "required": True
            }]
        },
        {
            "name": "yahoo",
            "description": "Search with Yahoo",
            "type": CommandOptionType.SUB_COMMAND,
            "options": [{
                "name": "query",
                "description": "Search query",
                "type": CommandOptionType.STRING,
                "required": True
            }]
        }
    ])
    def search(ctx, subcommand, *, query):
        "Search the Internet!"
        quoted = urllib.parse.quote_plus(query)
        if subcommand == "google":
            return f"https://google.com/search?q={quoted}"
        if subcommand == "bing":
            return f"https://bing.com/search?q={quoted}"
        if subcommand == "yahoo":
            return f"https://yahoo.com/search?q={quoted}"

As you can see, this approach is extremely verbose, so it isn't recommended.

The arguments passed to the function are:

* First positional argument: The :class:`.Context` object.
* Additional positional arguments: Subcommand group (if present), followed by subcommand (if present).
* Keyword arguments: The options passed to the command.

Full API
^^^^^^^^

.. autoclass:: flask_discord_interactions.SlashCommand
    :members:

Slash Command Groups
--------------------

The Discord API treats subcommands as options given to the main command.
However, this library provides an alternative way of declaring commands as
belonging to a :class:`.SlashCommandGroup` or a :class:`.SlashCommandSubgroup`.

To create a :class:`.SlashCommandGroup`, use the
:meth:`.DiscordInteractions.command_group` method:

.. code-block:: python

    comic = discord.command_group("comic")


    @comic.command()
    def xkcd(ctx, number: int):
        return f"https://xkcd.com/{number}/"


    @comic.command()
    def homestuck(ctx, number: int):
        return f"https://homestuck.com/story/{number}"

You can then use the :meth:`.SlashCommandGroup.command` decorator to
register subcommands.

Full API
^^^^^^^^

.. autoclass:: flask_discord_interactions.SlashCommandGroup
    :members:
    :inherited-members:
    :show-inheritance:


Slash Command Subgroups
-----------------------

You can also create subgroups that sit "in between" a
:class:`.SlashCommandGroup` and a :class:`.SlashCommand` using the
:meth:`.SlashCommandGroup.subgroup` decorator.

.. code-block:: python

    base = discord.command_group("base", "Convert a number between bases")

    base_to = base.subgroup("to", "Convert a number into a certain base")
    base_from = base.subgroup("from", "Convert a number out of a certian base")


    @base_to.command(name="bin")
    def base_to_bin(ctx, number: int):
        "Convert a number into binary"
        return Response(bin(number), ephemeral=True)


    @base_to.command(name="hex")
    def base_to_hex(ctx, number: int):
        "Convert a number into hexadecimal"
        return Response(hex(number), ephemeral=True)


    @base_from.command(name="bin")
    def base_from_bin(ctx, number: str):
        "Convert a number out of binary"
        return Response(int(number, base=2), ephemeral=True)


    @base_from.command(name="hex")
    def base_from_hex(ctx, number: str):
        "Convert a number out of hexadecimal"
        return Response(int(number, base=16), ephemeral=True)

Full API
^^^^^^^^

.. autoclass:: flask_discord_interactions.SlashCommandSubgroup
    :members:
    :inherited-members:
    :show-inheritance:

