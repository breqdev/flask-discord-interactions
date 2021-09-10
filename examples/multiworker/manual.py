"""
This file is an example of how to manually register commands to prevent the
worker thread rate limit problem.

To run this example, first register the commands:
    $ python3 examples/multiworker/manual.py register

Then, start the Gunicorn server (or whichever server you are using):
    $ gunicorn -w 4 examples.multiworker.manual:app

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


# THIS WILL NOT WORK
# it will attempt to register the commands at each worker thread
# and will fail due to rate limiting
# print("registering commands!")
# discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


# TRY THIS INSTEAD
if "register" in sys.argv:
    print("registering commands!")
    discord.update_commands(guild_id=os.environ["TESTING_GUILD"])
    sys.exit()


if __name__ == '__main__':
    app.run()
