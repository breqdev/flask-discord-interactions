import os
import sys
import time
import threading

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import (DiscordInteractions,  # noqa: E402
                                        Response)


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

discord.update_slash_commands()


# You can continue to send followup messages from background processes
# You can also send files now (although you can't with the initial response)
@discord.command()
def followup(ctx):
    def do_followup():
        print("Followup task started")
        time.sleep(5)

        print("Editing original message")
        ctx.edit("Editing my original message")
        time.sleep(5)

        print("Sending a file")
        ctx.send(Response(
            content="Sending a file",
            file=("README.md", open("README.md", "r"), "text/markdown")))
        time.sleep(5)

        print("Deleting original message")
        ctx.delete()
        time.sleep(5)

        print("Sending new message")
        new_message = ctx.send("Sending a new message")
        time.sleep(5)

        print("Editing new message")
        ctx.edit("Editing a new message", message=new_message)

    thread = threading.Thread(target=do_followup)
    thread.start()

    return "Sending an original message"


# You can set deferred=True to display a loading state to the user
@discord.command()
def delay(ctx, duration: int):
    def do_delay():
        time.sleep(duration)

        ctx.edit("Hiya!")

    thread = threading.Thread(target=do_delay)
    thread.start()

    return Response(deferred=True)


discord.set_route("/interactions")
discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
