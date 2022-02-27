import os
import sys

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import DiscordInteractions
from flask_discord_interactions.context import ApplicationCommandType


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

discord.update_commands()


# Simple command to mention a friend
# The target user is passed as an argument
# It is also accessible as `ctx.target`
@discord.command(name="High Five", type=ApplicationCommandType.USER)
def highFive(ctx, target):
    return f"<@{ctx.author.id}> wants to say hello to <@{target.id}>"


# Simple message command to repeat a message in bold
# The target message is passed as an argument (and as `ctx.target`)
@discord.command(name="Make it bold", type=ApplicationCommandType.MESSAGE)
def boldMessage(ctx, message):
    return f"**{message.content}**"


discord.set_route("/interactions")

discord.update_commands(guild_id=os.environ["TESTING_GUILD"])

if __name__ == "__main__":
    app.run()
