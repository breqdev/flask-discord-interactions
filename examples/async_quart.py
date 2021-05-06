import os
import sys
import time
import asyncio
import threading

from quart import Quart

# This is just here for the sake of examples testing
# to make sure that the imports work
# (you don't actually need it in your code)
sys.path.insert(1, ".")

import quart.flask_patch
from flask_discord_interactions import (DiscordInteractions, # noqa: E402
                                        Response)


app = Quart(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


discord.update_slash_commands()


# You can now use async functions!
@discord.command()
async def ping(ctx):
    "Respond with a friendly 'pong'!"
    return "Pong!"


# Non-async functions still work
@discord.command()
def pong(ctx):
    return "Ping!"


# You can use followups with asyncio
@discord.command()
async def wait(ctx, seconds: int):

    async def do_followup():
        await asyncio.sleep(seconds)
        await ctx.edit("Done!")
        await ctx.close()

    asyncio.create_task(do_followup())
    return Response(deferred=True)


# Normal followups work as well
@discord.command()
def wait_sync(ctx, seconds: int):

    def do_followup():
        time.sleep(seconds)
        ctx.edit("Done!")

    threading.Thread(target=do_followup).start()
    return Response(deferred=True)


# Use set_route_async if you want to use Quart
discord.set_route_async("/interactions")


discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
