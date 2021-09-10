import os
import sys

from flask import Flask
from redis import Redis
from rq import Queue

sys.path.insert(1, ".")

from flask_discord_interactions import DiscordInteractions, Response

from tasks import do_screenshot


app = Flask(__name__)
discord = DiscordInteractions(app)

# You will need to run a Redis instance in order to run this example
queue = Queue(connection=Redis())


app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

discord.update_commands()


@discord.command()
def screenshot(ctx, url: str):
    "Take a screenshot of a URL."
    queue.enqueue(do_screenshot, ctx.freeze(), url)
    return Response(deferred=True)


discord.set_route("/interactions")
discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
