Using Asyncio with Quart
========================

`Quart <https://pgjones.gitlab.io/quart/>`_ is a Python web framework designed
to have a similar API to Flask, but using :py:mod:`asyncio`.

.. code-block:: python

    from quart import Quart

    app = Quart(__name__)

    @app.route('/')
    async def hello():
        return 'hello'

    app.run()

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

    discord.update_slash_commands()

    @discord.command()
    async def ping(ctx):
        "Respond with a friendly 'pong'!"
        return "Pong!"

    # Non-async functions still work
    @discord.command()
    def pong(ctx):
        return "Ping!"

A special :class:`.AsyncContext` class is exposed to asynchronous commands.
This class makes :meth:`.AsyncContext.edit`, :meth:`.AsyncContext.send`, and
:meth:`.AsyncContext.delete` awaitable.

.. code-block:: python

    @discord.command()
    async def wait(ctx, seconds: int):

        async def do_followup():
            await asyncio.sleep(seconds)
            await ctx.edit("Done!")
            await ctx.close()

        asyncio.create_task(do_followup())
        return Response(deferred=True)

    # Normal followups use the normal Context
    @discord.command()
    def wait_sync(ctx, seconds: int):

        def do_followup():
            time.sleep(seconds)
            ctx.edit("Done!")

        threading.Thread(target=do_followup).start()
        return Response(deferred=True)

Full API
--------

.. autoclass:: flask_discord_interactions.AsyncContext(**kwargs)
    :show-inheritance:
    :members:
