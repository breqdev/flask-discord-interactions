import os
import sys

from flask import Flask

# This is just here for the sake of examples testing
# to make sure that the imports work
# (you don't actually need it in your code)
sys.path.insert(1, ".")

from flask_discord_interactions import DiscordInteractions  # noqa: E402
from flask_discord_interactions.context import ApplicationCommandType


app = Flask(__name__)
discord = DiscordInteractions(app)

# Find these in your Discord Developer Portal, store them as environment vars
app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


# Clear any existing global application commands
discord.update_commands()


# Simple command to mention a friend
# The target user is passed as an argument
@discord.command(name="High Five", type=ApplicationCommandType.USER)
def highFive(ctx, target):
    # we can also pull from ctx.target.id
    return f"<@{ctx.author.id}> wants to say hello to <@{target.id}>"


# This is the URL that your app will listen for Discord Interactions on
# Put this into the developer portal
discord.set_route("/interactions")


# Register application commands with this
# (omit guild_id parameter to register global commands,
# but note that these can take up to 1 hour to be registered)
# This also removes old/unused commands
discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
