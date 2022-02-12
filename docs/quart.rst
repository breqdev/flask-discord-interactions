.. _quart-page:

Using Asyncio with Quart
========================

`Quart <https://pgjones.gitlab.io/quart/>`_ is a Python web framework designed
to have a similar API to Flask, but using :mod:`asyncio`.

.. code-block:: python

    from quart import Quart

    app = Quart(__name__)

    @app.route('/')
    async def hello():
        return 'hello'

    app.run()

Monkey Patching
---------------

Flask-Discord-Interactions supports using Quart. This can provide a more
familiar development experience to those used to ``discord.py``'s
async commands.

Specifically, Quart supports
`monkey patching
<https://stackoverflow.com/questions/5626193/what-is-monkey-patching>`_
to allow Flask extensions to run with Quart. The specifics of this are
`in this tutorial
<https://pgjones.gitlab.io/quart/tutorials/flask_ext_tutorial.html>`_.

Flask-Discord-Interactions will work with this monkey patching. Additionally,
this library has some extra logic to handle mixing async and non-async
commands, and to allow awaiting when handling followup messages.

.. code-block:: python

    from quart import Quart

    import quart.flask_patch
    from flask_discord_interactions import DiscordInteractions

    app = Quart(__name__)
    discord = DiscordInteractions(app)

    discord.update_commands()

    @discord.command()
    async def ping(ctx):
        "Respond with a friendly 'pong'!"
        return "Pong!"

    # Non-async functions still work
    @discord.command()
    def pong(ctx):
        return "Ping!"

Use an Async Route Handler
--------------------------

If you want to use async commands in Flask-Discord-Interactions, then the
library needs to register an asynchronous handler for the interactions
endpoint. This is what allows Flask-Discord-Interactions to ``await``
your function handler.

If you are using Flask-Discord-Interactions with Quart, you need to call
:meth:`.DiscordInteractions.set_route_async` instead of
:meth:`.DiscordInteractions.set_route`.

.. code-block:: python

    discord.set_route_async("/interactions")

Context in Async Commands
-------------------------

A special :class:`.AsyncContext` class is exposed to asynchronous commands.
This class makes :meth:`.AsyncContext.edit`, :meth:`.AsyncContext.send`, and
:meth:`.AsyncContext.delete` awaitable.

.. code-block:: python

    @discord.command()
    async def wait(ctx, seconds: int):

        async def do_followup():
            await asyncio.sleep(seconds)
            await ctx.edit("Done!")

        asyncio.create_task(do_followup())
        return Message(deferred=True)

    # Normal followups use the normal Context
    @discord.command()
    def wait_sync(ctx, seconds: int):

        def do_followup():
            time.sleep(seconds)
            ctx.edit("Done!")

        threading.Thread(target=do_followup).start()
        return Message(deferred=True)

When creating command groups and subgroups, you will only get an
:class:`.AsyncContext` if you provide the ``is_async=True`` flag.

.. code-block:: python

    toplevel = discord.command_group("toplevel", is_async=True)
    secondlevel = toplevel.subgroup("secondlevel", is_async=True)

    @secondlevel.command()
    async def thirdlevel(ctx):
        async def do_followup():
            print(type(ctx))
            await asyncio.sleep(1)
            await ctx.edit(f"Hello, {ctx.author.display_name}!")

        asyncio.create_task(do_followup())
        return Message(deferred=True)

Full API
--------

.. autoclass:: flask_discord_interactions.AsyncContext(**kwargs)
    :show-inheritance:
    :members:
