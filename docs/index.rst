Flask-Discord-Interactions
==========================

Flask-Discord-Interactions is a Flask (or `Quart <https://pgjones.gitlab.io/quart/>`_) extension that lets you write Discord Slash Commands using a decorator syntax similar to Flask's ``@app.route()`` or Discord.py's ``@bot.command()``.

.. code-block:: python

    @discord.command()
    def ping(ctx):
        "Respond with a friendly 'pong'!"
        return "Pong!"


Features
--------

- Define commands with a declarative syntax
- Register commands with the Discord API
- Add Discord commands to a Flask app
- Handle webhook verification
- Send followup messages with webhooks
- Use ``async``/``await`` (with Quart)

Installation
------------

.. code-block:: bash

    pip3 install flask-discord-interactions

Since this library is new, and Discord Slash Commands are in beta, the API of this library might not be particularly stable. I strongly suggest you pin this library to a specific version when you deploy, and test your code after updates.

Documentation
-------------

.. toctree::
    :maxdepth: 2

    api.rst
    tutorials.rst

How is this different from ``discord-py-slash-command``?
--------------------------------------------------------

``Discord.py`` and ``discord-py-slash-command`` use a bot user and a websocket to connect to Discord, just like a regular Discord bot. It's a nice way to add support for slash commands to an existing Discord bot, or if you need to use a bot user to manage channels, reactions, etc.

However, for simple bots, using webhooks instead of websockets can let your bot scale better and use less resources. You can deploy a webhook-based bot behind a load balancer and scale it up or down as needed without needing to worry about sharding or dividing up guilds between the app processes.

Contribute
----------

- GitHub: https://github.com/Breq16/flask-discord-interactions

License
-------

The project is licensed under the MIT license.
