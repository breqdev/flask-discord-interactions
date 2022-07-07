.. _options-page:

Options
=======

Discord allows Slash Commands to receive a variety of different option types.
Each option has a name, description, and type.

To specify options with Flask-Discord-Interactions, you can use type
annotations. This syntax should feel familiar to users of Discord.py.

.. code-block:: python

    @discord.command(annotations={"message": "The message to repeat"})
    def repeat(ctx, message: str = "Hello!"):
        "Repeat the message (and escape mentions)"
        return Message(
            f"{ctx.author.display_name} says {message}!",
            allowed_mentions={"parse": []},
        )

The ``annotations`` parameter is used to provide a description for each option
(they default to "no description"). See :meth:`.DiscordInteractions.command`
for more information about the decorator.

Primitives
----------

You can use ``str``, ``int``, ``float``, or ``bool`` for string, integer,
number, and boolean options.

.. code-block:: python

    @discord.command()
    def add_one(ctx, number: int):
        return Message(str(number + 1), ephemeral=True)


    @discord.command()
    def and_gate(ctx, a: bool, b: bool):
        return f"{a} AND {b} is {a and b}"

Discord Models
--------------

For User, Channel, Role and Attachment options, you can receive an object with context
information about the option:

.. code-block:: python

    @discord.command()
    def has_role(ctx, user: Member, role: Role):
        if role.id in user.roles:
            return f"Yes, user {user.display_name} has role {role.name}."
        else:
            return f"No, user {user.display_name} does not have role {role.name}."

Choices
-------

To specify a list of choices the user can choose from, you can use Python's
:class:`enum.Enum` class.

.. code-block:: python

    class Animal(enum.Enum):
        Dog = "dog"
        Cat = "cat"


    @discord.command(annotations={"choice": "Your favorite animal"})
    def favorite(ctx, choice: Animal):
        "What is your favorite animal?"
        return f"{ctx.author.display_name} chooses {choice}!"

Note that you can use the same enum in multiple commands if they share the same
choices:

.. code-block:: python

    @discord.command(annotations={"choice": "The animal you hate the most"})
    def hate(ctx, choice: Animal):
        "What is the animal you hate the most?"
        return f"{ctx.author.display_name} hates {choice}s."

You can also use an :class:`enum.IntEnum` to receive the value as an integer
instead of a string:

.. code-block:: python

    class BigNumber(enum.IntEnum):
        thousand = 1_000
        million  = 1_000_000
        billion  = 1_000_000_000
        trillion = 1_000_000_000_000


    @discord.command(annotations={"number": "A big number"})
    def big_number(ctx, number: BigNumber):
        "Print out a large number"
        return f"One more than the number is {number+1}."

Explicit Options
----------------

If all of this magic doesn't fit your use case, there's an escape hatch you can
use to have full control over the data sent to Discord. Pass a list of ``dict`` s
or :class:`.Option` objects to the ``options`` argument when registering a
command:

.. code-block:: python

    @discord.command(
        options=[
            Option(
                name="message", type=str, description="The message to repeat", required=True
            ),
            Option(
                name="times",
                type=int,
                description="How many times to repeat the message",
                required=True,
            ),
        ]
    )
    def repeat_many(ctx, message: str, times: int):
        return " ".join([message] * times)

Full API
--------

.. autoclass:: flask_discord_interactions.Option
    :members:

.. autoclass:: flask_discord_interactions.CommandOptionType
    :members:
    :undoc-members:
    :member-order: bysource

|

.. autoclass:: flask_discord_interactions.Channel(**kwargs)
    :members:

|

.. autoclass:: flask_discord_interactions.Attachment
    :members:

|

.. autoclass:: flask_discord_interactions.ChannelType
    :members:
    :undoc-members:
    :member-order: bysource

|

.. autoclass:: flask_discord_interactions.User(**kwargs)
    :members:

|

.. autoclass:: flask_discord_interactions.Member(**kwargs)
    :members:
    :show-inheritance:

|

.. autoclass:: flask_discord_interactions.Role(**kwargs)
    :members:
