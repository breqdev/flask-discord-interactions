.. _workers:

Pitfalls with Multiple Workers
==============================

Does your bot work fine locally, but throw an error like this when you deploy
it?

.. code-block:: text

    [2021-07-29 14:00:00 +0000] [12] [ERROR] Exception in worker process
    Traceback (most recent call last):
    File "/usr/local/lib/python3.9/site-packages/flask_discord_interactions/discord.py", line 273, in update_slash_commands
        response.raise_for_status()
    File "/usr/local/lib/python3.9/site-packages/requests/models.py", line 953, in raise_for_status
        raise HTTPError(http_error_msg, response=self)
    requests.exceptions.HTTPError: 429 Client Error: Too Many Requests for url: https://discord.com/api/v9/applications/[...]

There are many potential pitfalls when using this library, where code can work fine
with one worker process but crash when scaled horizontally.

Rate Limiting
-------------

If you're deploying to an environment with multiple concurrent workers, you may
run into a situation where each worker will independently attempt to register
your application's slash commands with Discord. When this happens, there's a
good chance you'll get rate-limited!

Issue Reproduction
^^^^^^^^^^^^^^^^^^

You can see this issue by running an example with ``gunicorn -w 4`` or similar.
This will run four workers, each one will send a separate request to the
Discord API, and some of them will get rate-limited and crash.

Background
^^^^^^^^^^

Most of the examples for this library will call
``discord.update_slash_commands`` when the Flask app initializes. This can be
useful in a development environment: every time you restart your Flask app,
it will ensure that any changes in your commands are sent to Discord.

However, this becomes a problem if you want to serve your app with more than
one worker.
**Since each worker runs in an isolated environment, there isn't a reliable way
for Flask-Discord-Interactions to "coordinate" command registration across
multiple workers. Thus, this task left is up to you.**

Here are some general approaches you can use to handle command registration for
your app.

Approach 1: Manual Update
^^^^^^^^^^^^^^^^^^^^^^^^^

You can manually run ``discord.update_slash_commands`` before deploying your
app. For convenience, you could put this behind a command line argument:

.. code-block:: python


    import sys
    from flask import Flask
    from flask_discord_interactions import DiscordInteractions

    app = Flask(__name__)
    discord = DiscordInteractions(app)

    # ... configure your app and define your commands here ...

    if "register" in sys.argv:
        discord.update_slash_commands()
        sys.exit()


    if __name__ == '__main__':
        app.run()

You can run ``python3 app.py register`` (or similar) on your development
machine once to register the slash commands with Discord, then
``gunicorn app:app`` (or similar) on your production server to serve your app
without doing command registration.

This option is the most versatile, since it does not depend on any specific
web server or hosting setup.

Approach 2: Server Hooks
^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::
    *Note that if your application relies on parallelization beyond just one worker
    pool, this approach probably won't work for you.* For instance, if you're
    running multiple Heroku dynos / Docker containers / VM instances, each with its
    own separate web server, then each container will still make its own API
    requests, and you'll likely still see rate-limiting. **For this reason, for
    more complex deployments, it is recommended that you use a manual
    approach.**

Some Python web servers provide "hooks" that allow you to execute code when
certain server events happen. This usually includes when the server starts,
when a new worker starts, and when the web server closes. These often must be
defined in a separate configuration file. For this example, we will focus on
Gunicorn.

Gunicorn allows you to specify a configuration file with the ``-c [filename]``
command-line argument. This file can define an ``on_starting`` function that
will be executed exactly once when the server starts. This is where you can
register your commands with Discord.

You will need to make sure that your application module does not call
``discord.update_slash_commands`` when it is invoked:

.. code-block:: python

    # filename: app.py
    import sys
    from flask import Flask
    from flask_discord_interactions import DiscordInteractions

    app = Flask(__name__)
    discord = DiscordInteractions(app)

    # ... configure your app and define your commands here ...
    # but do NOT call `discord.update_slash_commands`

    if __name__ == '__main__':
        app.run()

Then, you will need to create a configuration file for Gunicorn:

.. code-block:: python

    # filename: app_conf.py
    from app import discord

    def on_starting(server):
        discord.update_slash_commands()

(Note that your import structure may vary depending on your application
structure.)

Finally, specify your configuration file when you run Gunicorn:

.. code-block:: bash

    $ gunicorn -c app_conf.py app:app

Custom IDs
----------

When declaring a custom ID handler without specifying the custom ID,
te :meth:`.DiscordInteractions.custom_handler` decorator will
actually generate a custom ID string itself (a :py:func:`uuid.uuid4`). It will return
this custom ID string in place of the function.

This strategy works great for development, but can lead to some frustrating
behavior in production:

- Every time your app is restarted, old custom handlers will no longer function. This is likely desirable in development, but can cause issues in production.
- If you deploy multiple instances/workers of your application, then they will not share the same custom IDs. This can lead to many issues, such as failure for one worker to process Interactions related to messages sent on another worker.

To avoid these issues, it is recommended that you specify a specific custom ID in these scenarios.

Instead of this:

.. code-block:: python

    @discord.custom_handler()
    def handle_my_interaction(ctx, interaction_id, current_count: int):
        ...


Try this:

.. code-block:: python

    @discord.custom_handler("handle my cool interaction")
    def handle_my_interaction(ctx, interaction_id, current_count: int):
        ...

But be mindful: your custom ID, plus whatever state you want to add
(see :ref:`storing-state-custom-id`), must fit within 100 characters!
