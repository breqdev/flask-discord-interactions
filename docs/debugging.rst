Debugging with an HTTP Client
=============================

This section describes how you may debug your bot locally by issuing commands
through tools such as `curl <https://curl.se/>`_, `Postman <https://www.postman.com/>`_,
or any other HTTP client.

It is assumed you already know the basics of setting up a bot. If not, see :ref:`tutorial-page`.

Configuration
-------------

Messages sent from Discord to your bot are signed and are verified when received. Having to
calculate the signature for your request can be time consuming and shouldn't be needed in a local
environment.

A config parameter ``DONT_VALIDATE_SIGNATURE`` is provided which when set to ``True`` will bypass
signature verification. This should only be set in debug mode and never in production.

Another config parameter ``DONT_REGISTER_WITH_DISCORD`` may be set to ``True`` to bypass registering
your slash commands with Discord when launched. Registering too many times in succession may result
in being temporarily limited by Discord. For local debugging it is not needed.

Example
-------

The following is simple example of a bot that will disable signature verification and Discord
registration.

It exposes one command ``/ping`` with an optional ``pong`` parameter.

.. code-block:: python

    import os
    import sys

    from flask import Flask

    sys.path.insert(1, ".")

    from flask_discord_interactions import DiscordInteractions

    app = Flask(__name__)
    discord = DiscordInteractions(app)

    app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
    app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
    app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]
    app.config["DONT_VALIDATE_SIGNATURE"] = True
    app.config["DONT_REGISTER_WITH_DISCORD"] = True

    discord.update_slash_commands()

    @discord.command()
    def ping(ctx, pong: str = 'pong'):
        f"Respond with a friendly 'pong'!"
        return f"{pong} with no signature verification!"

    discord.set_route("/interactions")
    discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])

    if __name__ == '__main__':
        app.run()

Testing
-------

Assuming your bot is running at ``http://127.0.0.1:5000`` and uses the ``/interactions`` route, the
below is a simple example of calling ``/ping`` with a ``pong`` parameter set to ``Pong``.

This is only a subset of the available JSON that may be passed in, but is the minimal needed
for this example to work.

.. code-block:: sh

    $ curl --location --request POST 'http://127.0.0.1:5000/interactions' --header 'Content-Type: application/json' --data-raw '{
        "id": 1,
        "channel_id": "",
        "guild_id": "",
        "token": "",
        "data": {
            "id": 1,
            "name": "ping",
            "options": [
                {
                    "type": 1,
                    "name": "Pong"
                }
            ]
        },
        "member": {
            "id": 1,
            "nick": "",
            "user": {
                "id": 1,
                "username": "test"
            }
        }
    }'

In Postman, you would issue a POST request to ``http://127.0.0.1:5000/interactions`` setting the
header ``Content-Type: application/json`` and your message as a raw JSON body.

In the Curl example above, the value given to the ``--data-raw`` parameter would be the JSON body
content, without the single quotes at the start and end.