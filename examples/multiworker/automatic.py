"""
This file is an example of how to use Gunicorn hooks to register commands to
prevent the worker thread rate limit problem.

Start the Gunicorn server with:
    $ gunicorn \\
        -w 4 \\
        -c examples/multiworker/automatic_conf.py \\
        examples.multiworker.automatic:app

"""

import os
import sys

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import DiscordInteractions  # noqa: E402


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


@discord.command()
def multiworkerping(ctx):
    "Respond with a friendly 'pong', served by one of many worker threads!"
    return "Pong!"


discord.set_route("/interactions")

if __name__ == "__main__":
    app.run()
