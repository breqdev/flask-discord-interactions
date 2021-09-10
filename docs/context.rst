.. _context-page:

Context
=======

This class provides context information about the incoming interaction as a
whole.

You normally would receive this as a ``ctx`` parameter to your
:class:`.Command` function, similar to in Discord.py.

.. code-block:: python

    @discord.command()
    def my_user_id(ctx):
        "Show your user ID"
        return f"Your ID is {ctx.author.id}"

This object is always passed in as the first positional argument to your
command function. You shouldn't ever need to create one yourself.

You can also use this object to send followup messages, edit messages, and
delete messages:

.. code-block:: python

    @discord.command()
    def delay(ctx, duration: int):
        def do_delay():
            time.sleep(duration)

            ctx.edit("Hi! I waited for you :)")

        thread = threading.Thread(target=do_delay)
        thread.start()

        return Message(deferred=True)

Pass in either a :class:`.Message` object or a string (which will be converted
into a :class:`.Message` object. See :ref:`response-page` for more details.

Full API
--------

.. autoclass:: flask_discord_interactions.Context
    :members:

