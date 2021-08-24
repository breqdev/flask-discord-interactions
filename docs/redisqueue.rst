Using RQ for Background Tasks
=============================

If your bot is performing long-running background tasks, you might want to use
a library like `RQ <https://python-rq.org/>`_ to schedule and run your tasks.
This is useful if you want your tasks to run on a separate process than your
Flask web server. It also provides more performance and (arguably) a cleaner
API than manually starting threads directly from your Flask routes.

Getting Started with RQ
-----------------------

First, you'll need RQ installed:

.. code-block:: bash

    pip3 install rq redis

Then, you'll need a Redis database to manage the queue. Redis has a
`quickstart guide <https://redis.io/topics/quickstart>`_ that can help with
this.

Note that RQ does not work under Windows. If you are developing on a Windows
machine, please use `WSL <https://docs.microsoft.com/en-us/windows/wsl/install-win10>`_.

Structuring your app
--------------------

Your RQ worker needs to be able to import any tasks you enqueue. For this
reason, it is best if you define your tasks in a separate file, say ``tasks.py``:

.. code-block:: python
    :caption: tasks.py

    import requests
    from flask_discord_interactions import Response


    def do_screenshot(ctx, url):
        response = requests.get(
            "https://shot.screenshotapi.net/screenshot",
            params={
                "url": url,
                "output": "image",
                "file_type": "png",
                "wait_for_event": "load"
            },
            stream=True
        )

        response.raw.decode_content = True

        ctx.edit(Response(content="Your screenshot is ready!"))

        ctx.send(Response(
            file=("screenshot.png", response.raw, "image/png")
        ))

Then, in your app module, you can create a Queue object and enqueue your tasks
in your commands:

.. code-block:: python
    :caption: app.py

    import os
    import sys

    from flask import Flask
    from redis import Redis
    from rq import Queue

    from flask_discord_interactions import DiscordInteractions, Response

    from tasks import do_screenshot

    app = Flask(__name__)
    discord = DiscordInteractions(app)

    queue = Queue(connection=Redis())

    app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
    app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
    app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

    @discord.command()
    def screenshot(ctx, url: str):
        "Take a screenshot of a URL."
        queue.enqueue(do_screenshot, ctx.freeze(), url)
        return Response(deferred=True)

    discord.set_route("/interactions")
    discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])


    if __name__ == '__main__':
        app.run()


A couple things to note here:

1. We create a Queue using the default name and with a new Redis connection.
   This is where you could customize your Redis config or your Queue config.
   The defaults are fine for local development, but you might want to use an
   external Redis server in production.

2. We enqueue tasks using ``queue.enqueue`` within our commands.
   To do this, we need to create a Pickleable version of the Context object
   with :meth:`.Context.freeze`. This object lacks some features that would
   normally be present in a Context object. This is necessary to send the
   Context object between processes to the RQ worker.

Finally, we need to define our worker.

.. code-block:: python
    :caption: worker.py

    import sys

    from redis import Redis
    from rq import Worker

    import flask_discord_interactions

    worker = Worker(["default"], connection=Redis())
    worker.work()

You can also start a worker from the command line (see the
`RQ docs <https://python-rq.org/>`_, but defining our worker script ourselves
allows us to preload the ``flask_discord_interactions`` module (and configure
import paths if that presents an issue).


Running your app
----------------

To run your app, you'll need to start your Flask app, your Redis server, and
your RQ worker. For deployment, you might want to run your Flask app and your
RQ worker in two different containers or machines, as long as your Redis server
is reachable from both.
