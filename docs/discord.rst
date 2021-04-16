Discord
=======

The :class:`.DiscordInteractions` and :class:`.DiscordInteractionsBlueprint`
classes manage a collection of :class:`.SlashCommand` s for you.

DiscordInteractions
-------------------



Generally, the first thing you want to do in your application is create your
Flask app and then your :class:`.DiscordInteractions` object:

.. code-block:: python

    from flask import Flask
    from flask_discord_interactions import DiscordInteractions

    app = Flask(__name__)
    discord = DiscordInteractions(app)

Then, you need to provide your authentication information for Discord. You
must provide:

* Client ID of your application
* Public Key assigned to your application (used to authenticate incoming webhooks from Discord)
* Client Secret of your application (used to request an OAuth2 token and register slash commands)

For a more tutorial-style explaination of this, see :ref:`tutorial-page`.

.. code-block:: python

    import os

    app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
    app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
    app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

Next, define your commands using the :meth:`.DiscordInteractions.command`
decorator and :meth:`.DiscordInteractions.command_group` function. For more
information about defining commands, see :ref:`command-page`.

.. code-block:: python

    @discord.command()
    def ping(ctx):
        "Respond with a friendly 'pong'!"
        return "Pong!"

Next, set the URL path that your app will listen for Discord Interactions on.
This is the part that you will enter into the Discord Developer Portal.

You could use the root URL ``"/"``, but you might want to pick a different path
like ``"/interactions"``. That way, you can serve your bot's website at ``"/"``
from the same Flask app.

.. code-block:: python

    discord.set_route("/interactions")

Finally, you need to register the slash commands with Discord.
:meth:`.DiscordInteractions.update_slash_commands` will automatically get
the list of currently registered slash commands, delete any that are no longer
defined, update any that have changed, and register any newly-defined ones.
*Note that this may take a while due to Discord rate-limiting, especially
if you are running your bot for the first time.*

You can optionally pass in a ``guild_id`` parameter. This will register
the commands in a specific guild instead of registering them globally.
This is the recommended approach for testing, since registering new global
commands can take up to 1 hour.

.. code-block:: python

    discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])

Now, like any other Flask app, all that's left to do is:

.. code-block:: python

    if __name__ == '__main__':
        app.run()

Running this code should serve your app locally. For production,
your app can be deployed like any other Flask app (using ``gunicorn``, etc).

Full API
^^^^^^^^

.. autoclass:: flask_discord_interactions.DiscordInteractions
    :members:
    :show-inheritance:
    :inherited-members:

Blueprints
----------

Similarly to Flask, you can use Blueprints to split your bot's commands
across multiple files. You can't use Flask Blueprints for this, because all
interactions from Discord are sent to the same URL. However, this library
provides a :class:`.DiscordInteractionsBlueprint` class which you can use
similarly to a Flask blueprint.

Here's an example of a simple echo bot split into two files.

.. code-block:: python
    :caption: echo.py

    from flask_discord_interactions import DiscordInteractionsBlueprint

    bp = DiscordInteractionsBlueprint()

    @bp.command()
    def echo(ctx, text: str):
        "Repeat a string"
        return f"*Echooo!!!* {text}"


.. code-block:: python
    :caption: main.py

    import os

    from flask import Flask
    from flask_discord_interactions import DiscordInteractions

    from echo import bp as echo_bp

    app = Flask(__name__)
    discord = DiscordInteractions(app)

    app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
    app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
    app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

    discord.register_blueprint(echo_bp)


    discord.set_route("/interactions")
    discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])

    if __name__ == '__main__':
        app.run()

As your app grows, Blueprints are a great way to keep things organized.
Note that you can also use the
:meth:`.DiscordInteractionsBlueprint.command_group` method to create a
command group, just like with the :class:`.DiscordInteractions` object.

Full API
^^^^^^^^

.. autoclass:: flask_discord_interactions.DiscordInteractionsBlueprint
    :members:
